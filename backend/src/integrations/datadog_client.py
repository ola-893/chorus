"""
Datadog integration client for metrics and logging.
"""
from typing import Dict, Any, Optional, List
import time
from datetime import datetime
import json
import logging

try:
    from datadog_api_client import ApiClient, Configuration
    from datadog_api_client.v2.api.logs_api import LogsApi
    from datadog_api_client.v2.model.http_log import HTTPLog
    from datadog_api_client.v2.model.http_log_item import HTTPLogItem
    from datadog_api_client.v1.api.metrics_api import MetricsApi
    from datadog_api_client.v1.model.metrics_payload import MetricsPayload
    from datadog_api_client.v1.model.series import Series
    from datadog_api_client.v1.model.point import Point
except ImportError:
    ApiClient = None
    Configuration = None
    LogsApi = None
    HTTPLog = None
    HTTPLogItem = None
    MetricsApi = None
    MetricsPayload = None
    Series = None
    Point = None

from ..config import settings
from ..error_handling import CircuitBreaker, SystemRecoveryError

logger = logging.getLogger(__name__)

# Circuit breaker for Datadog API calls
datadog_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30.0,
    expected_exception=Exception
)

class DatadogClient:
    """
    Client for interacting with Datadog API for metrics and logs.
    """
    
    def __init__(self):
        """Initialize Datadog client."""
        self.enabled = settings.datadog.enabled
        self.api_key = settings.datadog.api_key
        self.app_key = settings.datadog.app_key
        self.site = settings.datadog.site
        
        self.api_client = None
        self.logs_api = None
        self.metrics_api = None
        
        if self.enabled and self.api_key and self.app_key:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Datadog API client."""
        if not ApiClient:
            logger.warning("datadog-api-client not installed. Datadog integration disabled.")
            self.enabled = False
            return

        try:
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = self.api_key
            configuration.api_key["appKeyAuth"] = self.app_key
            configuration.server_variables["site"] = self.site
            
            self.api_client = ApiClient(configuration)
            self.logs_api = LogsApi(self.api_client)
            self.metrics_api = MetricsApi(self.api_client)
            
            logger.info("Datadog client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Datadog client: {e}")
            self.enabled = False

    @datadog_circuit_breaker
    def send_log(self, message: str, level: str = "INFO", context: Optional[Dict[str, Any]] = None, source: str = "chorus-backend"):
        """
        Send a log entry to Datadog.
        
        Args:
            message: Log message content
            level: Log level (INFO, WARN, ERROR, etc.)
            context: Additional context dictionary
            source: Log source
        """
        if not self.enabled or not self.logs_api:
            return

        try:
            body = HTTPLog(
                [
                    HTTPLogItem(
                        message=message,
                        ddsource=source,
                        ddtags=f"env:{settings.environment.value}",
                        service="chorus-conflict-predictor",
                        status=level,
                        additional_properties=context or {},
                    )
                ]
            )
            
            self.logs_api.submit_log(body)
            
        except Exception as e:
            # Don't crash app on logging failure, just log to local stderr
            logger.error(f"Failed to send log to Datadog: {e}")
            raise  # Let circuit breaker handle the failure

    @datadog_circuit_breaker
    def send_metric(self, metric_name: str, value: float, tags: Optional[List[str]] = None, metric_type: str = "gauge"):
        """
        Send a metric to Datadog.
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            tags: List of tags (e.g., ["env:prod", "region:us-east-1"])
            metric_type: Type of metric (gauge, count, rate)
        """
        if not self.enabled or not self.metrics_api:
            return

        try:
            current_tags = [f"env:{settings.environment.value}"]
            if tags:
                current_tags.extend(tags)
            
            body = MetricsPayload(
                series=[
                    Series(
                        metric=metric_name,
                        points=[Point([datetime.now().timestamp(), value])],
                        tags=current_tags,
                        type=metric_type,
                    )
                ]
            )
            
            self.metrics_api.submit_metrics(body)
            
        except Exception as e:
            logger.error(f"Failed to send metric to Datadog: {e}")
            raise  # Let circuit breaker handle the failure

    def track_trust_score_change(self, agent_id: str, old_score: int, new_score: int, reason: str):
        """
        Track agent trust score changes.
        """
        try:
            self.send_metric(
                "chorus.agent.trust_score",
                float(new_score),
                tags=[f"agent_id:{agent_id}"],
                metric_type="gauge"
            )
        except SystemRecoveryError:
            # Circuit breaker is open, gracefully degrade
            logger.debug(f"Datadog circuit breaker open, skipping trust score metric for {agent_id}")
        
        try:
            self.send_log(
                f"Trust score changed for agent {agent_id}: {old_score} -> {new_score}",
                level="INFO",
                context={
                    "agent_id": agent_id,
                    "old_score": old_score,
                    "new_score": new_score,
                    "reason": reason,
                    "change": new_score - old_score
                }
            )
        except SystemRecoveryError:
            # Circuit breaker is open, gracefully degrade
            logger.debug(f"Datadog circuit breaker open, skipping trust score log for {agent_id}")

    def track_conflict_prediction(self, conflict_id: str, risk_score: float, affected_agents: List[str]):
        """
        Track conflict predictions.
        """
        try:
            self.send_metric(
                "chorus.conflict.risk_score",
                risk_score,
                tags=[f"conflict_id:{conflict_id}"],
                metric_type="gauge"
            )
        except SystemRecoveryError:
            # Circuit breaker is open, gracefully degrade
            logger.debug(f"Datadog circuit breaker open, skipping conflict prediction metric for {conflict_id}")
        
        try:
            self.send_log(
                f"Conflict predicted with risk score {risk_score}",
                level="WARN" if risk_score > settings.conflict_prediction.risk_threshold else "INFO",
                context={
                    "conflict_id": conflict_id,
                    "risk_score": risk_score,
                    "affected_agents": affected_agents
                }
            )
        except SystemRecoveryError:
            # Circuit breaker is open, gracefully degrade
            logger.debug(f"Datadog circuit breaker open, skipping conflict prediction log for {conflict_id}")

# Global instance
datadog_client = DatadogClient()
