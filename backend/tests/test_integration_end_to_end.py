"""
End-to-end integration tests for the complete agent conflict predictor system.

These tests verify the complete pipeline from agent simulation through conflict
prediction to intervention and quarantine actions.
"""
import pytest
import time
import threading
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.prediction_engine.system_integration import ConflictPredictorSystem
from src.prediction_engine.models.core import (
    AgentIntention, ConflictAnalysis, ResourceType, GameState, ContentionEvent
)
from src.prediction_engine.simulator import AgentNetwork
from src.prediction_engine.intervention_engine import intervention_engine
from src.prediction_engine.trust_manager import trust_manager
from src.prediction_engine.quarantine_manager import quarantine_manager
from src.integrations.kafka_client import KafkaOperationError


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Integration tests for complete system workflows."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Patch RedisClient to avoid connection errors
        self.redis_patcher = patch('src.prediction_engine.redis_client.RedisClient')
        self.mock_redis_cls = self.redis_patcher.start()
        
        # Setup mock instance
        self.mock_redis = self.mock_redis_cls.return_value
        # Use a dict to simulate storage
        self.storage = {}
        
        def mock_set(key, value, **kwargs):
            self.storage[key] = value
            return True
            
        def mock_get(key):
            return self.storage.get(key)
            
        def mock_delete(key):
            if key in self.storage:
                del self.storage[key]
                return 1
            return 0
            
        def mock_set_json(key, value, **kwargs):
            import json
            from datetime import datetime
            
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, o):
                    if isinstance(o, datetime):
                        return o.isoformat()
                    return super().default(o)
                    
            self.storage[key] = json.dumps(value, cls=DateTimeEncoder)
            return True
            
        def mock_get_json(key):
            import json
            val = self.storage.get(key)
            return json.loads(val) if val else None
            
        def mock_exists(key):
            return 1 if key in self.storage else 0
            
        self.mock_redis.set.side_effect = mock_set
        self.mock_redis.get.side_effect = mock_get
        self.mock_redis.delete.side_effect = mock_delete
        self.mock_redis.set_json.side_effect = mock_set_json
        self.mock_redis.get_json.side_effect = mock_get_json
        self.mock_redis.exists.side_effect = mock_exists
        self.mock_redis.keys.side_effect = lambda p: [k for k in self.storage.keys() if k.startswith(p.replace('*', ''))]

        # We must inject our mock into the existing singleton instances.
        from src.prediction_engine.trust_manager import trust_manager
        from src.prediction_engine.quarantine_manager import quarantine_manager
        
        trust_manager.score_manager.redis_client = self.mock_redis
        trust_manager.redis_client = self.mock_redis
        quarantine_manager.redis_client = self.mock_redis
        
        # Pre-initialize agent_001 for trust tests
        self.mock_redis.exists.side_effect = lambda k: 1 if k == "trust_score:agent_001" or k in self.storage else 0
        self.storage["trust_score:agent_001"] = "100"
        
    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'system') and self.system:
            self.system.stop_system()
            
        if hasattr(self, 'redis_patcher'):
            self.redis_patcher.stop()
    
    def test_complete_simulation_to_intervention_workflow(self):
        """Test the complete workflow from agent simulation to intervention."""
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            system.start_system(agent_count=5)
            status = system.get_system_status()
            assert status["system_running"] is True
            assert status["total_agents"] == 5
            
            time.sleep(5.0)
    
            intentions = system.agent_network.get_all_intentions()
            assert len(intentions) > 0, "Agents should have generated intentions"
            
            with patch('src.prediction_engine.system_integration.intervention_engine') as mock_intervention:
                mock_result = Mock()
                mock_result.success = True
                mock_result.agent_id = "agent_001"
                mock_intervention.process_conflict_analysis.return_value = mock_result
                
                system.simulate_conflict_scenario()
                assert mock_intervention.process_conflict_analysis.called
            
        finally:
            system.stop_system()
    
    @patch('src.prediction_engine.gemini_client.genai')
    def test_gemini_integration_to_quarantine_workflow(self, mock_genai):
        """Test workflow from Gemini API analysis to quarantine action."""
        mock_response = Mock()
        mock_response.text = "RISK_SCORE: 0.85"
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            system.start_system(agent_count=3)
            time.sleep(1.0)
            
            intentions = system.agent_network.get_all_intentions()
            
            with patch('src.prediction_engine.gemini_client.GeminiClient') as MockGeminiClient:
                mock_client_instance = MockGeminiClient.return_value
                mock_analysis = ConflictAnalysis(
                    risk_score=0.85, confidence_level=0.95, affected_agents=["agent_1"],
                    predicted_failure_mode="CDN cache stampede", nash_equilibrium=None, timestamp=datetime.now()
                )
                mock_client_instance.analyze_conflict_risk.return_value = mock_analysis
                client = MockGeminiClient()
                analysis = client.analyze_conflict_risk(intentions)
            
            result = intervention_engine.process_conflict_analysis(analysis)
            
            assert result is not None
            assert result.success is True
            
            quarantined_agents = quarantine_manager.get_quarantined_agents()
            assert len(quarantined_agents) > 0
            
        finally:
            system.stop_system()
    def test_high_concurrency_agent_simulation(self):
        """Test system with a high volume of concurrent agent interactions."""
        # Create a system with a large number of agents to test concurrency
        system = ConflictPredictorSystem()
        self.system = system

        try:
            # Start the system with a higher agent count
            system.start_system(agent_count=25)
            
            # Allow the simulation to run for a period to observe concurrent behavior
            time.sleep(10)
            
            # Verify that the system remains stable
            status = system.get_system_status()
            assert status["system_running"] is True
            assert status["total_agents"] == 25
            
            # Ensure that agents are operating and generating intentions
            intentions = system.agent_network.get_all_intentions()
            assert len(intentions) > 0, "Agents should be active and generating intentions"
            
        finally:
            # Stop the system to clean up resources
            system.stop_system()

    def test_event_sourcing_integration(self):
        """Test that events are correctly logged by the EventLogManager."""
        with patch('src.event_sourcing.EventLogManager.log_event') as mock_log_event:
            system = ConflictPredictorSystem()
            self.system = system
            
            try:
                system.start_system(agent_count=2)
                time.sleep(1.0)
                
                analysis = ConflictAnalysis(
                    risk_score=0.95,
                    confidence_level=0.9,
                    affected_agents=["agent_1"],
                    predicted_failure_mode="Test failure",
                    nash_equilibrium=None,
                    timestamp=datetime.now()
                )
                
                intervention_engine.process_conflict_analysis(analysis)
                time.sleep(0.5)
                
                mock_log_event.assert_called()
                
                # Check the logged event
                call_args, _ = mock_log_event.call_args
                event = call_args[0]
                
                assert event.type == 'quarantine'
                assert event.data['agent_id'] == 'agent_1'

            finally:
                system.stop_system()

    def test_full_flow_to_dashboard_update(self):
        """Test the full flow from agent action to a dashboard update via WebSocket."""
        with patch('src.api.websocket_handler.WebSocketHandler.send_to_dashboard') as mock_send_to_dashboard:
            system = ConflictPredictorSystem()
            self.system = system
            
            try:
                system.start_system(agent_count=3)
                time.sleep(1.0)
                
                # Simulate a conflict high enough to trigger an intervention
                analysis = ConflictAnalysis(
                    risk_score=0.9,
                    confidence_level=0.9,
                    affected_agents=["agent_1"],
                    predicted_failure_mode="Test failure",
                    nash_equilibrium=None,
                    timestamp=datetime.now()
                )
                
                intervention_engine.process_conflict_analysis(analysis)
                
                # Let the system process the intervention and send the update
                time.sleep(0.5)
                
                mock_send_to_dashboard.assert_called()
                
                # Inspect the call arguments
                call_args, _ = mock_send_to_dashboard.call_args
                message = call_args[0]
                
                assert message['type'] == 'quarantine_event'
                assert message['data']['agent_id'] == 'agent_1'
                assert message['data']['action'] == 'quarantine'

            finally:
                system.stop_system()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
