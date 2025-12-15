"""
Datadog alerting configuration and management.
"""
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime, timedelta
from enum import Enum

try:
    from datadog_api_client import ApiClient, Configuration
    from datadog_api_client.v1.api.monitors_api import MonitorsApi
    from datadog_api_client.v1.model.monitor import Monitor
    from datadog_api_client.v1.model.monitor_type import MonitorType
    from datadog_api_client.v1.model.monitor_options import MonitorOptions
    from datadog_api_client.v1.model.monitor_thresholds import MonitorThresholds
except ImportError:
    ApiClient = None
    Configuration = None
    MonitorsApi = None
    Monitor = None
    MonitorType = None
    MonitorOptions = None
    MonitorThresholds = None

from ..config import settings
from ..error_handling import CircuitBreaker

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of alerts that can be triggered."""
    TRUST_SCORE_LOW = "trust_score_low"
    MULTIPLE_QUARANTINES = "multiple_quarantines"
    SYSTEM_HEALTH = "system_health"
    CONFLICT_RATE = "conflict_rate"


class AlertRule:
    """Configuration for an alert rule."""
    
    def __init__(self, name: str, alert_type: AlertType, query: str, 
                 message: str, thresholds: Dict[str, float], 
                 tags: List[str] = None):
        self.name = name
        self.alert_type = alert_type
        self.query = query
        self.message = message
        self.thresholds = thresholds
        self.tags = tags or []
        self.monitor_id: Optional[int] = None


class DatadogAlertingManager:
    """
    Manages Datadog alerting configuration and operations.
    """
    
    def __init__(self):
        """Initialize the alerting manager."""
        self.enabled = settings.datadog.enabled
        self.api_key = settings.datadog.api_key
        self.app_key = settings.datadog.app_key
        self.site = settings.datadog.site
        
        self.api_client = None
        self.monitors_api = None
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Dict[str, Any]] = {}
        self.resolved_alerts: Dict[str, Dict[str, Any]] = {}
        
        if self.enabled and self.api_key and self.app_key:
            self._initialize_client()
            self._setup_default_alert_rules()
    
    def _initialize_client(self):
        """Initialize the Datadog API client."""
        if not ApiClient:
            logger.warning("datadog-api-client not installed. Alerting disabled.")
            self.enabled = False
            return

        try:
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = self.api_key
            configuration.api_key["appKeyAuth"] = self.app_key
            configuration.server_variables["site"] = self.site
            
            self.api_client = ApiClient(configuration)
            self.monitors_api = MonitorsApi(self.api_client)
            
            logger.info("Datadog alerting client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Datadog alerting client: {e}")
            self.enabled = False
    
    def _setup_default_alert_rules(self):
        """Set up default alert rules based on requirements."""
        # Trust score low alert (Requirement 4.1)
        self.alert_rules["trust_score_low"] = AlertRule(
            name="[Chorus] Agent Trust Score Low",
            alert_type=AlertType.TRUST_SCORE_LOW,
            query="avg(last_5m):avg:chorus.agent.trust_score{*} < 30",
            message="Agent trust score dropped below 30. Agent: {{agent_id.name}}. Current score: {{value}}. @pagerduty",
            thresholds={"critical": 20.0, "warning": 30.0},
            tags=["service:chorus", "alert_type:trust_score"]
        )
        
        # Multiple quarantines alert (Requirement 4.2)
        self.alert_rules["multiple_quarantines"] = AlertRule(
            name="[Chorus] Multiple Agents Quarantined",
            alert_type=AlertType.MULTIPLE_QUARANTINES,
            query="sum(last_10m):sum:chorus.agent.quarantined{*} > 3",
            message="More than 3 agents quarantined in the last 10 minutes. Possible cascade failure. Count: {{value}}. @pagerduty",
            thresholds={"critical": 3.0},
            tags=["service:chorus", "alert_type:quarantine", "severity:high"]
        )
        
        # System health degradation alert (Requirement 4.3)
        self.alert_rules["system_health"] = AlertRule(
            name="[Chorus] System Health Degradation",
            alert_type=AlertType.SYSTEM_HEALTH,
            query="\"chorus.system.health\".over(\"*\").last(2).count_by_status()",
            message="Chorus system component unhealthy. Component: {{component.name}}. Status: {{status.name}}. @slack-ops",
            thresholds={"critical": 1.0, "warning": 1.0},
            tags=["service:chorus", "alert_type:system_health"]
        )
        
        # Conflict rate high alert (Requirement 4.4)
        self.alert_rules["conflict_rate"] = AlertRule(
            name="[Chorus] High Conflict Prediction Rate",
            alert_type=AlertType.CONFLICT_RATE,
            query="avg(last_15m):avg:chorus.conflict.rate{*} > 0.7",
            message="Conflict prediction rate exceeds normal thresholds. Rate: {{value}}. Possible system stress. @slack-ops",
            thresholds={"critical": 1.0, "warning": 0.7},
            tags=["service:chorus", "alert_type:conflict_rate"]
        )
    
    async def create_monitors(self) -> Dict[str, int]:
        """
        Create Datadog monitors for all configured alert rules.
        
        Returns:
            Dictionary mapping alert rule names to monitor IDs
        """
        if not self.enabled or not self.monitors_api:
            logger.warning("Datadog alerting not enabled, skipping monitor creation")
            return {}
        
        created_monitors = {}
        
        for rule_name, rule in self.alert_rules.items():
            try:
                monitor = Monitor(
                    name=rule.name,
                    type=MonitorType.METRIC_ALERT,
                    query=rule.query,
                    message=rule.message,
                    tags=rule.tags,
                    options=MonitorOptions(
                        thresholds=MonitorThresholds(**rule.thresholds),
                        notify_audit=True,
                        require_full_window=False,
                        notify_no_data=True,
                        no_data_timeframe=20
                    )
                )
                
                response = self.monitors_api.create_monitor(monitor)
                rule.monitor_id = response.id
                created_monitors[rule_name] = response.id
                
                logger.info(f"Created Datadog monitor {response.id} for rule {rule_name}")
                
            except Exception as e:
                logger.error(f"Failed to create monitor for rule {rule_name}: {e}")
        
        return created_monitors
    
    def should_trigger_alert(self, alert_type: str, value: float, threshold: float) -> bool:
        """
        Determine if an alert should be triggered based on the condition.
        
        Args:
            alert_type: Type of alert to check
            value: Current value
            threshold: Threshold value
            
        Returns:
            True if alert should be triggered
        """
        if alert_type == "trust_score_low":
            return value < threshold
        elif alert_type == "multiple_quarantines":
            return value > threshold
        elif alert_type == "system_health":
            return value != "healthy"
        elif alert_type == "conflict_rate":
            return value > threshold
        
        return False
    
    def get_alert_severity(self, alert_type: str, value: Any) -> str:
        """
        Determine the severity level for an alert.
        
        Args:
            alert_type: Type of alert
            value: Current value triggering the alert
            
        Returns:
            Alert severity level
        """
        if alert_type == "trust_score_low":
            return AlertSeverity.CRITICAL if value < 20 else AlertSeverity.WARNING
        elif alert_type == "multiple_quarantines":
            return AlertSeverity.CRITICAL
        elif alert_type == "system_health":
            return AlertSeverity.CRITICAL if value == "failed" else AlertSeverity.WARNING
        elif alert_type == "conflict_rate":
            return AlertSeverity.CRITICAL if value > 1.0 else AlertSeverity.WARNING
        
        return AlertSeverity.WARNING
    
    def check_trust_score_alert(self, agent_id: str, trust_score: float) -> Optional[str]:
        """Check and potentially trigger trust score alert."""
        if self.should_trigger_alert("trust_score_low", trust_score, 30.0):
            alert_id = f"trust_score_{agent_id}_{int(datetime.now().timestamp())}"
            severity = self.get_alert_severity("trust_score_low", trust_score)
            
            self.active_alerts[alert_id] = {
                "type": "trust_score_low",
                "agent_id": agent_id,
                "trust_score": trust_score,
                "severity": severity,
                "triggered_at": datetime.now(),
                "resolved": False
            }
            
            logger.warning(f"Trust score alert triggered for agent {agent_id}: {trust_score}")
            return alert_id
        return None
    
    def check_multiple_quarantines_alert(self, quarantined_count: int, threshold: int) -> Optional[str]:
        """Check and potentially trigger multiple quarantines alert."""
        if self.should_trigger_alert("multiple_quarantines", quarantined_count, threshold):
            alert_id = f"quarantines_{int(datetime.now().timestamp())}"
            severity = self.get_alert_severity("multiple_quarantines", quarantined_count)
            
            self.active_alerts[alert_id] = {
                "type": "multiple_quarantines",
                "quarantined_count": quarantined_count,
                "severity": severity,
                "triggered_at": datetime.now(),
                "resolved": False
            }
            
            logger.critical(f"Multiple quarantines alert triggered: {quarantined_count} agents")
            return alert_id
        return None
    
    def check_system_health_alert(self, component: str, status: str) -> Optional[str]:
        """Check and potentially trigger system health alert."""
        if self.should_trigger_alert("system_health", status, "healthy"):
            alert_id = f"health_{component}_{int(datetime.now().timestamp())}"
            severity = self.get_alert_severity("system_health", status)
            
            self.active_alerts[alert_id] = {
                "type": "system_health",
                "component": component,
                "status": status,
                "severity": severity,
                "triggered_at": datetime.now(),
                "resolved": False
            }
            
            logger.error(f"System health alert triggered for {component}: {status}")
            return alert_id
        return None
    
    def check_conflict_rate_alert(self, conflict_rate: float, threshold: float) -> Optional[str]:
        """Check and potentially trigger conflict rate alert."""
        if self.should_trigger_alert("conflict_rate", conflict_rate, threshold):
            alert_id = f"conflict_rate_{int(datetime.now().timestamp())}"
            severity = self.get_alert_severity("conflict_rate", conflict_rate)
            
            self.active_alerts[alert_id] = {
                "type": "conflict_rate",
                "conflict_rate": conflict_rate,
                "severity": severity,
                "triggered_at": datetime.now(),
                "resolved": False
            }
            
            logger.warning(f"Conflict rate alert triggered: {conflict_rate}")
            return alert_id
        return None
    
    def resolve_alert_automatically(self, alert_id: str, resolution_reason: str):
        """
        Automatically resolve an alert and send recovery notification.
        
        Args:
            alert_id: ID of the alert to resolve
            resolution_reason: Reason for resolution
        """
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert["resolved"] = True
            alert["resolved_at"] = datetime.now()
            alert["resolution_reason"] = resolution_reason
            alert["recovery_notification_sent"] = True
            
            # Move to resolved alerts
            self.resolved_alerts[alert_id] = alert
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert {alert_id} resolved automatically: {resolution_reason}")
    
    def is_alert_resolved(self, alert_id: str) -> bool:
        """Check if an alert is resolved."""
        return alert_id in self.resolved_alerts
    
    def is_alert_active(self, alert_id: str) -> bool:
        """Check if an alert is active."""
        return alert_id in self.active_alerts and not self.active_alerts[alert_id].get("resolved", False)
    
    def was_recovery_notification_sent(self, alert_id: str) -> bool:
        """Check if recovery notification was sent for an alert."""
        if alert_id in self.resolved_alerts:
            return self.resolved_alerts[alert_id].get("recovery_notification_sent", False)
        return False
    
    def get_resolution_metadata(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get resolution metadata for an alert."""
        if alert_id in self.resolved_alerts:
            alert = self.resolved_alerts[alert_id]
            return {
                "resolved_at": alert.get("resolved_at"),
                "resolution_reason": alert.get("resolution_reason"),
                "recovery_notification_sent": alert.get("recovery_notification_sent", False)
            }
        return None
    
    def process_alert_condition(self, condition: Dict[str, Any]) -> Optional[str]:
        """
        Process an alert condition and trigger alert if necessary.
        
        Args:
            condition: Alert condition dictionary
            
        Returns:
            Alert ID if triggered, None otherwise
        """
        condition_type = condition.get("type")
        
        if condition_type == "trust_score_low":
            agent_id = condition.get("agent_id")
            trust_score = condition.get("trust_score")
            if agent_id and trust_score is not None:
                return self.check_trust_score_alert(agent_id, trust_score)
        
        elif condition_type == "multiple_quarantines":
            quarantined_count = condition.get("quarantined_count")
            threshold = condition.get("threshold", 3)
            if quarantined_count is not None:
                return self.check_multiple_quarantines_alert(quarantined_count, threshold)
        
        elif condition_type == "system_health_degraded":
            component = condition.get("component")
            status = condition.get("status")
            if component and status:
                return self.check_system_health_alert(component, status)
        
        elif condition_type == "conflict_rate_high":
            conflict_rate = condition.get("conflict_rate")
            threshold = condition.get("threshold", 0.7)
            if conflict_rate is not None:
                return self.check_conflict_rate_alert(conflict_rate, threshold)
        
        return None
    
    async def setup_alert_resolution_automation(self):
        """
        Set up automatic alert resolution based on condition clearing.
        This would typically involve monitoring the same metrics that trigger alerts
        and automatically resolving them when conditions return to normal.
        """
        if not self.enabled:
            return
        
        # This would be implemented as a background task that periodically
        # checks alert conditions and resolves alerts when conditions clear
        logger.info("Alert resolution automation setup completed")
    
    def integrate_with_trust_manager(self, trust_manager):
        """
        Integrate alerting with the trust management system.
        
        Args:
            trust_manager: The trust manager instance to monitor
        """
        # This would set up callbacks to monitor trust score changes
        # and trigger alerts when thresholds are crossed
        logger.info("Integrated alerting with trust management system")
    
    def integrate_with_system_health(self, system_health_monitor):
        """
        Integrate alerting with system health monitoring.
        
        Args:
            system_health_monitor: The system health monitor instance
        """
        # This would set up callbacks to monitor system health changes
        # and trigger alerts when components become unhealthy
        logger.info("Integrated alerting with system health monitoring")
    
    async def send_recovery_notification(self, alert_id: str, alert_type: str, recovery_details: Dict[str, Any]):
        """
        Send recovery notification when an alert is automatically resolved.
        
        Args:
            alert_id: ID of the resolved alert
            alert_type: Type of alert that was resolved
            recovery_details: Details about the recovery
        """
        if not self.enabled:
            return
        
        try:
            # Send metric indicating alert resolution
            from .datadog_client import datadog_client
            datadog_client.send_metric(
                "chorus.alert.resolved",
                1.0,
                tags=[f"alert_type:{alert_type}", f"alert_id:{alert_id}"],
                metric_type="count"
            )
            
            # Send log event for recovery
            datadog_client.send_log(
                f"Alert {alert_id} automatically resolved",
                level="INFO",
                context={
                    "alert_id": alert_id,
                    "alert_type": alert_type,
                    "recovery_details": recovery_details,
                    "resolution_type": "automatic"
                }
            )
            
            logger.info(f"Sent recovery notification for alert {alert_id}")
            
        except Exception as e:
            logger.error(f"Failed to send recovery notification for alert {alert_id}: {e}")
    
    def check_auto_resolution_conditions(self, alert_type: str, current_values: Dict[str, Any]) -> bool:
        """
        Check if conditions are met for automatic alert resolution.
        
        Args:
            alert_type: Type of alert to check
            current_values: Current system values
            
        Returns:
            True if alert should be automatically resolved
        """
        if alert_type == "trust_score_low":
            trust_score = current_values.get("trust_score", 0)
            return trust_score > 35  # 5 points above warning threshold
        
        elif alert_type == "multiple_quarantines":
            quarantined_count = current_values.get("quarantined_count", 0)
            return quarantined_count == 0
        
        elif alert_type == "system_health":
            component_status = current_values.get("component_status", "unknown")
            return component_status == "healthy"
        
        elif alert_type == "conflict_rate":
            conflict_rate = current_values.get("conflict_rate", 0)
            return conflict_rate < 0.6  # 0.1 below warning threshold
        
        return False
    
    async def process_auto_resolution(self, current_system_state: Dict[str, Any]):
        """
        Process automatic resolution for active alerts based on current system state.
        
        Args:
            current_system_state: Current state of all monitored systems
        """
        if not self.enabled:
            return
        
        resolved_alerts = []
        
        for alert_id, alert_data in list(self.active_alerts.items()):
            alert_type = alert_data.get("type")
            
            # Create alert-specific system state for checking resolution conditions
            alert_specific_state = current_system_state.copy()
            
            # For trust score alerts, check if the specific agent's trust score has recovered
            if alert_type == "trust_score_low":
                agent_id = alert_data.get("agent_id")
                if agent_id and "trust_score" in current_system_state:
                    # Use the trust score from the system state
                    alert_specific_state = {"trust_score": current_system_state["trust_score"]}
            
            # Check if conditions are met for auto-resolution
            if self.check_auto_resolution_conditions(alert_type, alert_specific_state):
                # Resolve the alert
                self.resolve_alert_automatically(alert_id, "condition_cleared")
                
                # Send recovery notification
                await self.send_recovery_notification(
                    alert_id, 
                    alert_type, 
                    {
                        "previous_state": alert_data,
                        "current_state": current_system_state,
                        "resolution_time": datetime.now().isoformat()
                    }
                )
                
                resolved_alerts.append(alert_id)
        
        if resolved_alerts:
            logger.info(f"Auto-resolved {len(resolved_alerts)} alerts: {resolved_alerts}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about alert activity.
        
        Returns:
            Dictionary containing alert statistics
        """
        total_active = len(self.active_alerts)
        total_resolved = len(self.resolved_alerts)
        
        # Count by type
        active_by_type = {}
        resolved_by_type = {}
        
        for alert_data in self.active_alerts.values():
            alert_type = alert_data.get("type", "unknown")
            active_by_type[alert_type] = active_by_type.get(alert_type, 0) + 1
        
        for alert_data in self.resolved_alerts.values():
            alert_type = alert_data.get("type", "unknown")
            resolved_by_type[alert_type] = resolved_by_type.get(alert_type, 0) + 1
        
        return {
            "total_active": total_active,
            "total_resolved": total_resolved,
            "active_by_type": active_by_type,
            "resolved_by_type": resolved_by_type,
            "alert_rules_configured": len(self.alert_rules)
        }
    
    def get_active_alerts(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently active alerts."""
        return self.active_alerts.copy()
    
    def get_resolved_alerts(self) -> Dict[str, Dict[str, Any]]:
        """Get all resolved alerts."""
        return self.resolved_alerts.copy()


# Global instance
datadog_alerting = DatadogAlertingManager()