#!/usr/bin/env python3
"""
Comprehensive Demo of Chorus Multi-Agent Immune System

This script demonstrates all major capabilities of the Chorus system:
1. Agent simulation and conflict prediction
2. Trust management and quarantine
3. Real-time monitoring dashboard
4. Integration with external services (Gemini, Datadog, Redis)
5. Intervention engine and safety mechanisms

Usage:
    python comprehensive_demo.py [--mode MODE] [--duration SECONDS]
    
Modes:
    - full: Complete system demo with all integrations (default)
    - simulation: Agent simulation and conflict prediction only
    - dashboard: CLI dashboard demonstration
    - api: REST API demonstration
    - integration: External service integration tests
"""

import asyncio
import argparse
import sys
import os
import time
import json
import subprocess
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from prediction_engine.simulator import AgentSimulator
from prediction_engine.cli_dashboard import CLIDashboard
from prediction_engine.system_integration import SystemIntegration
from prediction_engine.trust_manager import TrustManager
from prediction_engine.intervention_engine import InterventionEngine
from prediction_engine.gemini_client import GeminiClient
from prediction_engine.redis_client import RedisClient
from config import Config
from logging_config import setup_logging

class ComprehensiveDemo:
    """Comprehensive demonstration of the Chorus system capabilities."""
    
    def __init__(self, mode: str = "full", duration: int = 300):
        self.mode = mode
        self.duration = duration
        self.config = Config()
        self.logger = setup_logging()
        
        # Initialize components
        self.redis_client = None
        self.gemini_client = None
        self.trust_manager = None
        self.intervention_engine = None
        self.simulator = None
        self.dashboard = None
        self.system_integration = None
        
        # Demo state
        self.demo_start_time = None
        self.demo_stats = {
            'agents_created': 0,
            'conflicts_predicted': 0,
            'interventions_performed': 0,
            'trust_scores_updated': 0,
            'api_calls_made': 0
        }
    
    async def initialize_system(self):
        """Initialize all system components."""
        print("🚀 Initializing Chorus Multi-Agent Immune System...")
        
        try:
            # Initialize Redis client
            self.redis_client = RedisClient()
            await self.redis_client.connect()
            print("✅ Redis client connected")
            
            # Initialize Gemini client
            self.gemini_client = GeminiClient()
            print("✅ Gemini client initialized")
            
            # Initialize trust manager
            self.trust_manager = TrustManager(self.redis_client)
            print("✅ Trust manager initialized")
            
            # Initialize intervention engine
            self.intervention_engine = InterventionEngine(
                trust_manager=self.trust_manager,
                redis_client=self.redis_client
            )
            print("✅ Intervention engine initialized")
            
            # Initialize agent simulator
            self.simulator = AgentSimulator(
                trust_manager=self.trust_manager,
                intervention_engine=self.intervention_engine,
                gemini_client=self.gemini_client
            )
            print("✅ Agent simulator initialized")
            
            # Initialize system integration
            self.system_integration = SystemIntegration(
                simulator=self.simulator,
                trust_manager=self.trust_manager,
                intervention_engine=self.intervention_engine,
                gemini_client=self.gemini_client,
                redis_client=self.redis_client
            )
            print("✅ System integration initialized")
            
            print("🎯 System initialization complete!\n")
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            raise
    
    async def run_demo(self):
        """Run the comprehensive demo based on selected mode."""
        self.demo_start_time = datetime.now()
        
        print(f"🎬 Starting Chorus Demo - Mode: {self.mode.upper()}")
        print(f"⏱️  Duration: {self.duration} seconds")
        print("=" * 80)
        
        try:
            if self.mode == "full":
                await self.run_full_demo()
            elif self.mode == "simulation":
                await self.run_simulation_demo()
            elif self.mode == "dashboard":
                await self.run_dashboard_demo()
            elif self.mode == "api":
                await self.run_api_demo()
            elif self.mode == "integration":
                await self.run_integration_demo()
            else:
                raise ValueError(f"Unknown demo mode: {self.mode}")
                
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            raise
        finally:
            await self.cleanup()
            self.print_demo_summary()
    
    async def run_full_demo(self):
        """Run the complete system demonstration."""
        print("🌟 FULL SYSTEM DEMONSTRATION")
        print("This demo showcases all Chorus capabilities:\n")
        
        # Phase 1: System Health Check
        await self.demo_system_health()
        
        # Phase 2: Agent Simulation
        await self.demo_agent_simulation()
        
        # Phase 3: Conflict Prediction
        await self.demo_conflict_prediction()
        
        # Phase 4: Trust Management
        await self.demo_trust_management()
        
        # Phase 5: Intervention Engine
        await self.demo_intervention_engine()
        
        # Phase 6: Real-time Dashboard
        await self.demo_dashboard()
        
        # Phase 7: API Integration
        await self.demo_api_integration()
        
        # Phase 8: External Service Integration
        await self.demo_external_integrations()
    
    async def demo_system_health(self):
        """Demonstrate system health monitoring."""
        print("📊 PHASE 1: SYSTEM HEALTH MONITORING")
        print("-" * 50)
        
        # Check system components
        health_status = await self.system_integration.get_system_health()
        
        print("System Component Status:")
        for component, status in health_status.items():
            icon = "✅" if status["healthy"] else "❌"
            print(f"  {icon} {component}: {status['status']}")
            if not status["healthy"] and "error" in status:
                print(f"    └─ Error: {status['error']}")
        
        # Display configuration
        print(f"\nConfiguration:")
        print(f"  Trust Score Threshold: {self.config.trust_score_threshold}")
        print(f"  Conflict Risk Threshold: {self.config.conflict_risk_threshold}")
        print(f"  Max Agents: {self.config.max_agents}")
        
        await asyncio.sleep(3)
        print()
    
    async def demo_agent_simulation(self):
        """Demonstrate agent simulation capabilities."""
        print("🤖 PHASE 2: AGENT SIMULATION")
        print("-" * 50)
        
        # Create initial agents
        num_agents = 6
        print(f"Creating {num_agents} autonomous agents...")
        
        agents = []
        for i in range(num_agents):
            agent_id = f"demo_agent_{i+1:03d}"
            agent = await self.simulator.create_agent(agent_id)
            agents.append(agent)
            print(f"  ✅ Created {agent_id}")
            self.demo_stats['agents_created'] += 1
        
        print(f"\n📈 Agent Activity Simulation:")
        
        # Simulate agent interactions
        for round_num in range(3):
            print(f"\n  Round {round_num + 1}: Agent Interactions")
            
            # Simulate resource requests
            for agent in agents[:4]:  # First 4 agents request resources
                resource_type = ["cpu", "memory", "network", "storage"][round_num % 4]
                await self.simulator.simulate_resource_request(agent.agent_id, resource_type)
                print(f"    🔄 {agent.agent_id} requested {resource_type}")
            
            # Simulate message exchanges
            for i in range(2):
                sender = agents[i]
                receiver = agents[i + 1]
                await self.simulator.simulate_message_exchange(sender.agent_id, receiver.agent_id)
                print(f"    💬 {sender.agent_id} → {receiver.agent_id}")
            
            await asyncio.sleep(2)
        
        print(f"\n✅ Agent simulation complete - {len(agents)} agents active")
        await asyncio.sleep(2)
        print()
    
    async def demo_conflict_prediction(self):
        """Demonstrate conflict prediction using Gemini AI."""
        print("🔮 PHASE 3: CONFLICT PREDICTION")
        print("-" * 50)
        
        print("Analyzing agent interactions for potential conflicts...")
        
        # Get current agent states
        agents = await self.simulator.get_all_agents()
        
        # Create conflict scenarios
        scenarios = [
            {
                "name": "Resource Contention",
                "agents": [agents[0].agent_id, agents[1].agent_id, agents[2].agent_id],
                "resource": "cpu",
                "description": "Multiple agents competing for CPU resources"
            },
            {
                "name": "Communication Deadlock", 
                "agents": [agents[1].agent_id, agents[3].agent_id],
                "resource": "network",
                "description": "Circular dependency in message passing"
            },
            {
                "name": "Trust Score Degradation",
                "agents": [agents[4].agent_id],
                "resource": "trust",
                "description": "Agent showing suspicious behavior patterns"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n  🎯 Analyzing: {scenario['name']}")
            print(f"     Agents: {', '.join(scenario['agents'])}")
            print(f"     Context: {scenario['description']}")
            
            # Perform conflict analysis
            try:
                analysis = await self.gemini_client.analyze_conflict_potential(
                    agent_ids=scenario['agents'],
                    context=scenario['description']
                )
                
                risk_level = "LOW" if analysis.risk_score < 0.3 else "MODERATE" if analysis.risk_score < 0.7 else "HIGH"
                risk_icon = "🟢" if risk_level == "LOW" else "🟡" if risk_level == "MODERATE" else "🔴"
                
                print(f"     Result: {risk_icon} {risk_level} RISK ({analysis.risk_score:.1%})")
                print(f"     Prediction: {analysis.predicted_outcome}")
                
                if analysis.recommended_actions:
                    print(f"     Recommendations: {', '.join(analysis.recommended_actions)}")
                
                self.demo_stats['conflicts_predicted'] += 1
                self.demo_stats['api_calls_made'] += 1
                
            except Exception as e:
                print(f"     ⚠️  Analysis failed: {e}")
            
            await asyncio.sleep(2)
        
        print(f"\n✅ Conflict prediction complete - {self.demo_stats['conflicts_predicted']} scenarios analyzed")
        await asyncio.sleep(2)
        print()
    
    async def demo_trust_management(self):
        """Demonstrate trust scoring and management."""
        print("🛡️  PHASE 4: TRUST MANAGEMENT")
        print("-" * 50)
        
        agents = await self.simulator.get_all_agents()
        
        print("Current Trust Scores:")
        for agent in agents:
            trust_score = await self.trust_manager.get_trust_score(agent.agent_id)
            status_icon = "✅" if trust_score >= self.config.trust_score_threshold else "⚠️"
            print(f"  {status_icon} {agent.agent_id}: {trust_score}")
        
        print(f"\n🔄 Simulating trust score changes...")
        
        # Simulate positive behavior
        good_agent = agents[0]
        await self.trust_manager.update_trust_score(good_agent.agent_id, 10, "Successful resource sharing")
        new_score = await self.trust_manager.get_trust_score(good_agent.agent_id)
        print(f"  ⬆️  {good_agent.agent_id}: +10 (successful cooperation) → {new_score}")
        self.demo_stats['trust_scores_updated'] += 1
        
        # Simulate negative behavior
        bad_agent = agents[1]
        await self.trust_manager.update_trust_score(bad_agent.agent_id, -25, "Resource hoarding detected")
        new_score = await self.trust_manager.get_trust_score(bad_agent.agent_id)
        print(f"  ⬇️  {bad_agent.agent_id}: -25 (resource hoarding) → {new_score}")
        self.demo_stats['trust_scores_updated'] += 1
        
        # Simulate suspicious behavior
        suspicious_agent = agents[2]
        await self.trust_manager.update_trust_score(suspicious_agent.agent_id, -40, "Anomalous communication pattern")
        new_score = await self.trust_manager.get_trust_score(suspicious_agent.agent_id)
        print(f"  ⬇️  {suspicious_agent.agent_id}: -40 (suspicious activity) → {new_score}")
        self.demo_stats['trust_scores_updated'] += 1
        
        # Check for trust threshold violations
        print(f"\n🚨 Trust Threshold Monitoring (threshold: {self.config.trust_score_threshold}):")
        for agent in agents:
            trust_score = await self.trust_manager.get_trust_score(agent.agent_id)
            if trust_score < self.config.trust_score_threshold:
                print(f"  ⚠️  {agent.agent_id}: {trust_score} - BELOW THRESHOLD")
            else:
                print(f"  ✅ {agent.agent_id}: {trust_score} - OK")
        
        await asyncio.sleep(3)
        print()
    
    async def demo_intervention_engine(self):
        """Demonstrate intervention and quarantine capabilities."""
        print("🚫 PHASE 5: INTERVENTION ENGINE")
        print("-" * 50)
        
        agents = await self.simulator.get_all_agents()
        
        print("Monitoring for intervention triggers...")
        
        # Check for agents needing quarantine
        quarantine_candidates = []
        for agent in agents:
            trust_score = await self.trust_manager.get_trust_score(agent.agent_id)
            if trust_score < self.config.trust_score_threshold:
                quarantine_candidates.append((agent, trust_score))
        
        if quarantine_candidates:
            print(f"\n🎯 Found {len(quarantine_candidates)} agents requiring intervention:")
            
            for agent, trust_score in quarantine_candidates:
                print(f"\n  🚫 Quarantining {agent.agent_id} (trust score: {trust_score})")
                
                # Perform quarantine
                success = await self.intervention_engine.quarantine_agent(
                    agent_id=agent.agent_id,
                    reason=f"Trust score ({trust_score}) below threshold ({self.config.trust_score_threshold})",
                    confidence=0.95
                )
                
                if success:
                    print(f"     ✅ Quarantine successful")
                    print(f"     🔒 Agent isolated from network")
                    print(f"     📝 Intervention logged")
                    self.demo_stats['interventions_performed'] += 1
                else:
                    print(f"     ❌ Quarantine failed")
        else:
            print("  ✅ No agents require quarantine at this time")
        
        # Demonstrate conflict-based intervention
        print(f"\n🔍 Simulating high-risk conflict scenario...")
        
        high_risk_agents = agents[:3]
        conflict_analysis = {
            'risk_score': 0.85,
            'predicted_outcome': 'Cascading failure due to resource deadlock',
            'affected_agents': [a.agent_id for a in high_risk_agents],
            'recommended_actions': ['isolate_agents', 'redistribute_resources']
        }
        
        print(f"  🔴 HIGH RISK detected: {conflict_analysis['risk_score']:.1%}")
        print(f"  📊 Prediction: {conflict_analysis['predicted_outcome']}")
        print(f"  🎯 Affected agents: {', '.join(conflict_analysis['affected_agents'])}")
        
        # Perform preventive intervention
        for agent in high_risk_agents:
            print(f"  🚫 Preventive quarantine: {agent.agent_id}")
            await self.intervention_engine.quarantine_agent(
                agent_id=agent.agent_id,
                reason="Preventive isolation due to high conflict risk",
                confidence=0.85
            )
            self.demo_stats['interventions_performed'] += 1
        
        # Show quarantine status
        print(f"\n📊 Current Quarantine Status:")
        quarantined_agents = await self.intervention_engine.get_quarantined_agents()
        if quarantined_agents:
            for agent_id in quarantined_agents:
                print(f"  🔒 {agent_id}: QUARANTINED")
        else:
            print("  ✅ No agents currently quarantined")
        
        await asyncio.sleep(3)
        print()
    
    async def demo_dashboard(self):
        """Demonstrate the real-time CLI dashboard."""
        print("📊 PHASE 6: REAL-TIME DASHBOARD")
        print("-" * 50)
        
        print("Starting CLI dashboard for 15 seconds...")
        print("(Dashboard will show real-time system metrics)\n")
        
        # Initialize dashboard
        self.dashboard = CLIDashboard(
            system_integration=self.system_integration,
            refresh_interval=1.0
        )
        
        # Run dashboard for a short time
        dashboard_task = asyncio.create_task(self.dashboard.run())
        
        try:
            await asyncio.wait_for(dashboard_task, timeout=15.0)
        except asyncio.TimeoutError:
            dashboard_task.cancel()
            try:
                await dashboard_task
            except asyncio.CancelledError:
                pass
        
        print("\n✅ Dashboard demonstration complete")
        await asyncio.sleep(2)
        print()
    
    async def demo_api_integration(self):
        """Demonstrate REST API capabilities."""
        print("🌐 PHASE 7: API INTEGRATION")
        print("-" * 50)
        
        print("API endpoints available:")
        endpoints = [
            "GET /health - System health check",
            "GET /agents - List all agents",
            "GET /agents/{id}/trust-score - Get agent trust score",
            "POST /agents/{id}/quarantine - Quarantine an agent",
            "GET /conflicts/predict - Predict conflicts",
            "GET /dashboard/metrics - Dashboard metrics"
        ]
        
        for endpoint in endpoints:
            print(f"  📡 {endpoint}")
        
        # Simulate API calls
        print(f"\n🔄 Simulating API interactions...")
        
        # Health check
        health_status = await self.system_integration.get_system_health()
        print(f"  ✅ GET /health → {len(health_status)} components checked")
        self.demo_stats['api_calls_made'] += 1
        
        # Agent list
        agents = await self.simulator.get_all_agents()
        print(f"  ✅ GET /agents → {len(agents)} agents returned")
        self.demo_stats['api_calls_made'] += 1
        
        # Trust scores
        if agents:
            agent = agents[0]
            trust_score = await self.trust_manager.get_trust_score(agent.agent_id)
            print(f"  ✅ GET /agents/{agent.agent_id}/trust-score → {trust_score}")
            self.demo_stats['api_calls_made'] += 1
        
        # Dashboard metrics
        metrics = await self.system_integration.get_dashboard_metrics()
        print(f"  ✅ GET /dashboard/metrics → {len(metrics)} metrics returned")
        self.demo_stats['api_calls_made'] += 1
        
        print(f"\n✅ API integration demonstration complete")
        await asyncio.sleep(2)
        print()
    
    async def demo_external_integrations(self):
        """Demonstrate external service integrations."""
        print("🔌 PHASE 8: EXTERNAL SERVICE INTEGRATIONS")
        print("-" * 50)
        
        # Redis integration
        print("📊 Redis Integration:")
        try:
            redis_info = await self.redis_client.get_info()
            print(f"  ✅ Connected to Redis {redis_info.get('redis_version', 'unknown')}")
            print(f"  📈 Memory usage: {redis_info.get('used_memory_human', 'unknown')}")
            print(f"  🔑 Keys stored: {await self.redis_client.count_keys()}")
        except Exception as e:
            print(f"  ❌ Redis connection failed: {e}")
        
        # Gemini API integration
        print(f"\n🤖 Gemini AI Integration:")
        try:
            # Test API connectivity
            test_result = await self.gemini_client.test_connection()
            if test_result:
                print(f"  ✅ Gemini API connected")
                print(f"  🧠 Model: gemini-3-pro-preview")
                print(f"  📊 API calls made: {self.demo_stats['api_calls_made']}")
            else:
                print(f"  ❌ Gemini API connection failed")
        except Exception as e:
            print(f"  ❌ Gemini API error: {e}")
        
        # Datadog integration (if configured)
        print(f"\n📊 Datadog Integration:")
        if self.config.datadog_enabled:
            print(f"  ✅ Datadog monitoring enabled")
            print(f"  📈 Metrics being sent to Datadog")
            print(f"  🚨 Alerts configured for system events")
        else:
            print(f"  ⚠️  Datadog integration not configured")
        
        # ElevenLabs integration (if configured)
        print(f"\n🔊 ElevenLabs Integration:")
        if self.config.elevenlabs_enabled:
            print(f"  ✅ Voice alerts enabled")
            print(f"  🎙️  Text-to-speech for critical incidents")
        else:
            print(f"  ⚠️  ElevenLabs integration not configured")
        
        await asyncio.sleep(3)
        print()
    
    async def run_simulation_demo(self):
        """Run agent simulation demonstration only."""
        print("🤖 AGENT SIMULATION DEMO")
        print("-" * 50)
        
        await self.demo_agent_simulation()
        await self.demo_conflict_prediction()
    
    async def run_dashboard_demo(self):
        """Run dashboard demonstration only."""
        print("📊 DASHBOARD DEMO")
        print("-" * 50)
        
        # Create some agents first
        await self.demo_agent_simulation()
        await self.demo_dashboard()
    
    async def run_api_demo(self):
        """Run API demonstration only."""
        print("🌐 API DEMO")
        print("-" * 50)
        
        await self.demo_api_integration()
    
    async def run_integration_demo(self):
        """Run external integration demonstration only."""
        print("🔌 INTEGRATION DEMO")
        print("-" * 50)
        
        await self.demo_external_integrations()
    
    async def cleanup(self):
        """Clean up resources and connections."""
        print("\n🧹 Cleaning up resources...")
        
        try:
            if self.dashboard:
                await self.dashboard.stop()
            
            if self.simulator:
                await self.simulator.cleanup()
            
            if self.redis_client:
                await self.redis_client.disconnect()
            
            print("✅ Cleanup complete")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def print_demo_summary(self):
        """Print demonstration summary statistics."""
        duration = datetime.now() - self.demo_start_time if self.demo_start_time else timedelta(0)
        
        print("\n" + "=" * 80)
        print("📊 DEMO SUMMARY")
        print("=" * 80)
        print(f"Mode: {self.mode.upper()}")
        print(f"Duration: {duration.total_seconds():.1f} seconds")
        print(f"")
        print(f"Statistics:")
        print(f"  🤖 Agents Created: {self.demo_stats['agents_created']}")
        print(f"  🔮 Conflicts Predicted: {self.demo_stats['conflicts_predicted']}")
        print(f"  🚫 Interventions Performed: {self.demo_stats['interventions_performed']}")
        print(f"  🛡️  Trust Scores Updated: {self.demo_stats['trust_scores_updated']}")
        print(f"  📡 API Calls Made: {self.demo_stats['api_calls_made']}")
        print(f"")
        print("🎯 Demo completed successfully!")
        print("=" * 80)


def main():
    """Main entry point for the comprehensive demo."""
    parser = argparse.ArgumentParser(description="Chorus Multi-Agent Immune System Demo")
    parser.add_argument(
        "--mode", 
        choices=["full", "simulation", "dashboard", "api", "integration"],
        default="full",
        help="Demo mode to run"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Demo duration in seconds"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run the demo
    demo = ComprehensiveDemo(mode=args.mode, duration=args.duration)
    
    try:
        asyncio.run(demo.initialize_system())
        asyncio.run(demo.run_demo())
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()