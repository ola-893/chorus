"""
System integration module for connecting all components of the agent conflict predictor.
"""
import logging
from typing import Optional

from .simulator import AgentNetwork
from .intervention_engine import intervention_engine
from .quarantine_manager import quarantine_manager
from .trust_manager import trust_manager
from ..config import settings
from ..logging_config import get_agent_logger
from ..system_health import health_monitor
from ..error_handling import system_recovery_context

logger = logging.getLogger(__name__)
agent_logger = get_agent_logger(__name__)


class ConflictPredictorSystem:
    """
    Main system class that integrates all components of the agent conflict predictor.
    
    Provides a unified interface for starting and managing the complete system
    including agent simulation, conflict prediction, and intervention capabilities.
    """
    
    def __init__(self):
        """Initialize the complete system with all components."""
        # Initialize core components
        self.trust_manager = trust_manager
        self.quarantine_manager = quarantine_manager
        self.intervention_engine = intervention_engine
        
        # Initialize agent network with quarantine manager integration
        self.agent_network = AgentNetwork(
            min_agents=settings.agent_simulation.min_agents,
            max_agents=settings.agent_simulation.max_agents,
            quarantine_manager=self.quarantine_manager
        )
        
        # Connect intervention engine with quarantine manager
        self.intervention_engine.set_quarantine_manager(self.quarantine_manager)
        
        logger.info("Conflict predictor system initialized")
    
    def start_system(self, agent_count: Optional[int] = None) -> None:
        """
        Start the complete system.
        
        Args:
            agent_count: Number of agents to create (optional, uses random if None)
        """
        with system_recovery_context(
            component="system_integration",
            operation="start_system",
            fallback_action=self._emergency_shutdown
        ):
            agent_logger.log_agent_action(
                "INFO",
                "Starting conflict predictor system",
                action_type="system_startup",
                context={"agent_count": agent_count}
            )
            
            # Start health monitoring first
            health_monitor.start_monitoring()
            
            # Create and start agents
            if agent_count:
                self.agent_network.create_agents(agent_count)
            
            # Start agent simulation
            self.agent_network.start_simulation()
            
            agent_logger.log_agent_action(
                "INFO",
                "Conflict predictor system started successfully",
                action_type="system_started",
                context={"active_agents": len(self.agent_network.agents)}
            )
    
    def stop_system(self) -> None:
        """Stop the complete system."""
        with system_recovery_context(
            component="system_integration",
            operation="stop_system"
        ):
            agent_logger.log_agent_action(
                "INFO",
                "Stopping conflict predictor system",
                action_type="system_shutdown"
            )
            
            # Stop health monitoring
            health_monitor.stop_monitoring()
            
            # Stop agent simulation
            self.agent_network.stop_simulation()
            
            agent_logger.log_agent_action(
                "INFO",
                "Conflict predictor system stopped successfully",
                action_type="system_stopped"
            )
    
    def _emergency_shutdown(self) -> None:
        """Emergency shutdown procedure for system recovery."""
        try:
            agent_logger.log_agent_action(
                "CRITICAL",
                "Executing emergency shutdown",
                action_type="emergency_shutdown"
            )
            
            # Stop health monitoring
            health_monitor.stop_monitoring()
            
            # Force stop agent simulation
            if hasattr(self, 'agent_network') and self.agent_network:
                self.agent_network.stop_simulation()
            
            agent_logger.log_agent_action(
                "INFO",
                "Emergency shutdown completed",
                action_type="emergency_shutdown_complete"
            )
            
        except Exception as e:
            agent_logger.log_system_error(
                e,
                component="system_integration",
                operation="emergency_shutdown"
            )
    
    def get_system_status(self) -> dict:
        """
        Get current system status.
        
        Returns:
            Dictionary with system status information
        """
        try:
            active_agents = self.agent_network.get_active_agents()
            quarantined_agents = self.quarantine_manager.get_quarantined_agents()
            
            return {
                "system_running": self.agent_network.is_running,
                "total_agents": len(self.agent_network.agents),
                "active_agents": len(active_agents),
                "quarantined_agents": len(quarantined_agents),
                "quarantine_statistics": self.quarantine_manager.get_statistics(),
                "intervention_statistics": self.intervention_engine.get_statistics()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    def simulate_conflict_scenario(self) -> None:
        """
        Simulate a conflict scenario for testing purposes.
        
        This method can be used to trigger conflicts and test the intervention system.
        """
        try:
            logger.info("Simulating conflict scenario...")
            
            # Get current agent intentions
            intentions = self.agent_network.get_all_intentions()
            
            if not intentions:
                logger.warning("No agent intentions available for conflict simulation")
                return
            
            # For demonstration, we can manually trigger a high-risk scenario
            # In a real system, this would come from the Gemini API analysis
            from .models.core import ConflictAnalysis
            from datetime import datetime
            
            # Create a mock high-risk conflict analysis
            mock_analysis = ConflictAnalysis(
                risk_score=0.85,  # Above threshold
                confidence_level=0.9,
                affected_agents=[intention.agent_id for intention in intentions[:3]],
                predicted_failure_mode="Resource contention leading to cascading failure",
                nash_equilibrium=None,
                timestamp=datetime.now()
            )
            
            # Process through intervention engine
            result = self.intervention_engine.process_conflict_analysis(mock_analysis)
            
            if result and result.success:
                logger.info(f"Conflict scenario processed: quarantined agent {result.agent_id}")
            else:
                logger.warning("Conflict scenario processing failed or no action taken")
                
        except Exception as e:
            logger.exception(f"Error simulating conflict scenario: {e}")


# Global system instance
conflict_predictor_system = ConflictPredictorSystem()