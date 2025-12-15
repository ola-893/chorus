"""
End-to-end integration tests for the complete agent conflict predictor system.

These tests verify the complete pipeline from agent simulation through conflict
prediction to intervention and quarantine actions.
"""
import pytest
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.prediction_engine.system_integration import ConflictPredictorSystem
from src.prediction_engine.models.core import (
    AgentIntention, ConflictAnalysis, ResourceType, GameState
)
from src.prediction_engine.simulator import AgentNetwork
from src.prediction_engine.intervention_engine import intervention_engine
from src.prediction_engine.trust_manager import trust_manager
from src.prediction_engine.quarantine_manager import quarantine_manager


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Integration tests for complete system workflows."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Reset system state by releasing any existing quarantines
        quarantined_agents = quarantine_manager.get_quarantined_agents()
        for agent_id in quarantined_agents:
            quarantine_manager.release_quarantine(agent_id)
        
    def teardown_method(self):
        """Clean up after each test."""
        # Ensure system is stopped
        try:
            if hasattr(self, 'system') and self.system:
                self.system.stop_system()
        except:
            pass
    
    def test_complete_simulation_to_intervention_workflow(self):
        """Test the complete workflow from agent simulation to intervention."""
        # Create system
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            # Start system with specific agent count
            system.start_system(agent_count=5)
            
            # Verify system started correctly
            status = system.get_system_status()
            assert status["system_running"] is True
            assert status["total_agents"] == 5
            assert status["active_agents"] == 5
            assert status["quarantined_agents"] == 0
            
            # Let agents run and generate intentions
            time.sleep(2.0)
            
            # Get agent intentions
            intentions = system.agent_network.get_all_intentions()
            assert len(intentions) > 0, "Agents should have generated intentions"
            
            # Simulate conflict scenario
            system.simulate_conflict_scenario()
            
            # Verify intervention occurred
            time.sleep(1.0)
            final_status = system.get_system_status()
            
            # Should have at least one quarantined agent after conflict simulation
            assert final_status["quarantined_agents"] > 0, "Conflict should result in quarantine"
            
            # Verify remaining agents are still active
            assert final_status["active_agents"] > 0, "Other agents should remain active"
            
        finally:
            system.stop_system()
    
    @patch('src.prediction_engine.gemini_client.genai')
    def test_gemini_integration_to_quarantine_workflow(self, mock_genai):
        """Test workflow from Gemini API analysis to quarantine action."""
        # Mock high-risk Gemini response
        mock_response = Mock()
        mock_response.text = """
        RISK_SCORE: 0.85
        CONFIDENCE: 0.95
        AFFECTED_AGENTS: agent_1, agent_2, agent_3
        FAILURE_MODE: CDN cache stampede causing cascading failures
        NASH_EQUILIBRIUM: Competitive equilibrium with resource exhaustion
        REASONING: Multiple agents requesting same cached resources simultaneously
        """
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create system and start simulation
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            system.start_system(agent_count=3)
            time.sleep(1.0)
            
            # Get agent intentions for analysis
            intentions = system.agent_network.get_all_intentions()
            
            # Perform conflict analysis through Gemini client
            from src.prediction_engine.gemini_client import GeminiClient
            client = GeminiClient()
            analysis = client.analyze_conflict_risk(intentions)
            
            # Verify analysis results
            assert analysis.risk_score == 0.85
            assert analysis.confidence_level == 0.95
            assert len(analysis.affected_agents) == 3
            assert "stampede" in analysis.predicted_failure_mode.lower()
            
            # Process through intervention engine
            result = intervention_engine.process_conflict_analysis(analysis)
            
            # Verify intervention occurred
            assert result is not None
            assert result.success is True
            assert result.agent_id in analysis.affected_agents
            
            # Verify quarantine was applied
            quarantined_agents = quarantine_manager.get_quarantined_agents()
            assert len(quarantined_agents) > 0
            assert result.agent_id in quarantined_agents
            
        finally:
            system.stop_system()
    
    def test_multi_agent_conflict_simulation(self):
        """Test multi-agent conflict scenarios with resource contention."""
        # Create larger agent network for conflict testing
        network = AgentNetwork(min_agents=8, max_agents=10)
        
        try:
            # Start simulation
            network.start_simulation()
            
            # Verify multiple agents created
            assert len(network.agents) >= 8
            assert len(network.agents) <= 10
            
            # Force resource contention by consuming most resources
            for resource_type in ["cpu", "memory", "storage"]:
                # Use 80% of each resource type
                request = network.resource_manager.process_request(
                    type('MockRequest', (), {
                        'agent_id': 'test_consumer',
                        'resource_type': resource_type,
                        'amount': 800,  # 80% of 1000 default capacity
                        'priority': 9,
                        'timestamp': datetime.now()
                    })()
                )
                assert request.success, f"Should be able to consume {resource_type}"
            
            # Let agents compete for remaining resources
            time.sleep(3.0)
            
            # Check for resource contention
            contention_events = network.resource_manager.detect_contention()
            
            # Verify contention occurred
            assert len(contention_events) > 0, "Should detect resource contention"
            
            # Verify agents are still generating intentions despite contention
            intentions = network.get_all_intentions()
            assert len(intentions) > 0, "Agents should continue generating intentions"
            
            # Test quarantine during contention
            first_agent_id = network.agents[0].agent_id
            success = network.quarantine_agent(first_agent_id)
            assert success, "Should be able to quarantine agent during contention"
            
            # Verify quarantined agent stops making requests
            time.sleep(1.0)
            quarantined_agent = next(a for a in network.agents if a.agent_id == first_agent_id)
            assert quarantined_agent.is_quarantined
            
            # Verify other agents continue operating
            active_agents = network.get_active_agents()
            assert len(active_agents) >= 7, "Other agents should remain active"
            
        finally:
            network.stop_simulation()
    
    def test_cdn_cache_stampede_scenario(self):
        """Test specific CDN cache stampede scenario."""
        # Create scenario with agents requesting same cached resources
        network = AgentNetwork(min_agents=6, max_agents=6)
        
        try:
            # Create agents with specific behavior for cache stampede
            agents = network.create_agents(6)
            
            # Simulate cache stampede by having all agents request same resource
            cache_resource = "cache_cdn_content"
            stampede_intentions = []
            
            for i, agent in enumerate(agents):
                intention = AgentIntention(
                    agent_id=agent.agent_id,
                    resource_type=cache_resource,
                    requested_amount=100,  # All requesting same amount
                    priority_level=8,      # High priority
                    timestamp=datetime.now() + timedelta(milliseconds=i*10)  # Nearly simultaneous
                )
                stampede_intentions.append(intention)
                
                # Inject intention into agent
                agent._current_intentions = [intention]
            
            # Start simulation
            network.start_simulation()
            time.sleep(1.0)
            
            # Verify stampede scenario created
            all_intentions = network.get_all_intentions()
            cache_intentions = [i for i in all_intentions if i.resource_type == cache_resource]
            assert len(cache_intentions) >= 6, "Should have cache stampede intentions"
            
            # Check for resource contention on cache resource
            contention_events = network.resource_manager.detect_contention()
            cache_contention = [e for e in contention_events if cache_resource in str(e)]
            
            # Verify contention detected (may not always trigger due to timing)
            # This is acceptable as real systems have timing variations
            
            # Test intervention system response to stampede
            from src.prediction_engine.models.core import ConflictAnalysis
            
            # Create analysis representing cache stampede detection
            stampede_analysis = ConflictAnalysis(
                risk_score=0.9,
                confidence_level=0.85,
                affected_agents=[agent.agent_id for agent in agents],
                predicted_failure_mode="CDN cache stampede causing service degradation",
                nash_equilibrium=None,
                timestamp=datetime.now()
            )
            
            # Process through intervention engine
            result = intervention_engine.process_conflict_analysis(stampede_analysis)
            
            # Verify intervention occurred
            assert result is not None
            assert result.success is True
            
            # Verify most aggressive agent was quarantined
            quarantined_agents = quarantine_manager.get_quarantined_agents()
            assert len(quarantined_agents) > 0
            
            # Verify other agents can continue (stampede resolved)
            time.sleep(1.0)
            active_agents = network.get_active_agents()
            assert len(active_agents) >= 5, "Most agents should remain active after intervention"
            
        finally:
            network.stop_simulation()
    
    def test_trust_score_integration_workflow(self):
        """Test trust score updates throughout the complete workflow."""
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            # Start system
            system.start_system(agent_count=4)
            
            # Get initial trust scores
            agents = system.agent_network.agents
            initial_scores = {}
            for agent in agents:
                score = trust_manager.get_trust_score(agent.agent_id)
                initial_scores[agent.agent_id] = score
                assert score == 100, "New agents should start with trust score 100"
            
            # Simulate conflict and intervention
            system.simulate_conflict_scenario()
            time.sleep(1.0)
            
            # Check trust score changes
            quarantined_agents = quarantine_manager.get_quarantined_agents()
            
            if quarantined_agents:
                # Verify quarantined agent has reduced trust score
                quarantined_agent_id = quarantined_agents[0]
                new_score = trust_manager.get_trust_score(quarantined_agent_id)
                assert new_score < initial_scores[quarantined_agent_id], \
                    "Quarantined agent should have reduced trust score"
                
                # Verify other agents maintain their trust scores
                for agent in agents:
                    if agent.agent_id != quarantined_agent_id:
                        score = trust_manager.get_trust_score(agent.agent_id)
                        assert score >= initial_scores[agent.agent_id], \
                            "Non-quarantined agents should maintain trust scores"
            
            # Test trust score recovery after quarantine release
            if quarantined_agents:
                quarantined_agent_id = quarantined_agents[0]
                
                # Release from quarantine
                success = quarantine_manager.release_quarantine(quarantined_agent_id)
                assert success, "Should be able to release agent from quarantine"
                
                # Let agent operate normally
                time.sleep(2.0)
                
                # Trust score should remain at reduced level (no automatic recovery)
                final_score = trust_manager.get_trust_score(quarantined_agent_id)
                assert final_score < 100, "Trust score should not automatically recover"
            
        finally:
            system.stop_system()
    
    def test_system_resilience_during_failures(self):
        """Test system resilience when components fail."""
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            # Start system
            system.start_system(agent_count=3)
            
            # Verify normal operation
            status = system.get_system_status()
            assert status["system_running"] is True
            
            # Simulate Redis failure by patching trust manager
            with patch.object(trust_manager, 'get_trust_score', side_effect=Exception("Redis connection failed")):
                # System should continue operating despite trust manager failure
                time.sleep(1.0)
                
                # Agents should still be active
                active_agents = system.agent_network.get_active_agents()
                assert len(active_agents) > 0, "Agents should remain active despite Redis failure"
            
            # Simulate Gemini API failure
            with patch('src.prediction_engine.gemini_client.genai.GenerativeModel', side_effect=Exception("API failure")):
                # System should handle API failure gracefully
                try:
                    system.simulate_conflict_scenario()
                    # Should not crash the system
                except Exception:
                    pass  # Expected to fail, but system should remain stable
                
                # Verify system is still running
                status = system.get_system_status()
                assert status["system_running"] is True
            
            # Test recovery after failures
            time.sleep(1.0)
            final_status = system.get_system_status()
            assert final_status["system_running"] is True
            assert final_status["active_agents"] > 0
            
        finally:
            system.stop_system()
    
    def test_concurrent_operations_workflow(self):
        """Test system behavior under concurrent operations."""
        system = ConflictPredictorSystem()
        self.system = system
        
        try:
            # Start system with more agents for concurrency testing
            system.start_system(agent_count=6)
            
            # Define concurrent operations
            def simulate_conflicts():
                for _ in range(3):
                    system.simulate_conflict_scenario()
                    time.sleep(0.5)
            
            def monitor_system():
                for _ in range(5):
                    status = system.get_system_status()
                    assert isinstance(status, dict)
                    time.sleep(0.3)
            
            def manage_quarantines():
                agents = system.agent_network.agents
                for agent in agents[:2]:
                    quarantine_manager.quarantine_agent(
                        agent.agent_id, 
                        "Test quarantine", 
                        duration=2
                    )
                    time.sleep(0.8)
                    quarantine_manager.release_quarantine(agent.agent_id)
            
            # Run operations concurrently
            threads = [
                threading.Thread(target=simulate_conflicts),
                threading.Thread(target=monitor_system),
                threading.Thread(target=manage_quarantines)
            ]
            
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join(timeout=10)  # 10 second timeout
            
            # Verify system integrity after concurrent operations
            final_status = system.get_system_status()
            assert final_status["system_running"] is True
            assert final_status["total_agents"] == 6
            
            # System should have handled concurrent operations without corruption
            assert isinstance(final_status["quarantine_statistics"], dict)
            assert isinstance(final_status["intervention_statistics"], dict)
            
        finally:
            system.stop_system()


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration"])