import asyncio
import uvicorn
import random
import sys
import os
from datetime import datetime

# Add current directory to path so we can import src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.main import create_app
from src.system_lifecycle import lifecycle_manager
from src.prediction_engine.trust_manager import trust_manager
from src.event_bus import event_bus

# Create app instance
app = create_app(lifecycle_manager)

async def simulate_system_activity():
    """Simulate active agents and system events."""
    print("🚀 Starting Chorus Simulation Engine...")
    
    # Initialize some agents
    agents = [f"agent_{i:03d}" for i in range(1, 10)]
    for agent in agents:
        trust_manager.get_trust_score(agent)

    while True:
        try:
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # 1. Simulate Trust Score Updates
            agent = random.choice(agents)
            
            # Determine adjustment based on current score to create interesting patterns
            current = trust_manager.get_trust_score(agent)
            
            if random.random() < 0.15: 
                # Occasional bad behavior
                adj = random.randint(-15, -5)
                reason = "resource_conflict_detected"
            elif random.random() < 0.05:
                # Critical failure
                adj = -30
                reason = "security_policy_violation"
            else:
                # Normal cooperation
                adj = random.randint(1, 5)
                reason = "successful_cooperation"
                
            # This triggers event_bus.publish("trust_score_update") internally in TrustManager
            trust_manager.update_trust_score(agent, adj, reason)
            print(f"🔹 Updated {agent}: {current} -> {current+adj} ({reason})")

            # 2. Simulate Conflict Predictions (occasionally)
            if random.random() < 0.1:
                risk = random.uniform(0.6, 0.95)
                affected = random.sample(agents, 2)
                event_bus.publish("conflict_prediction", {
                    "type": "conflict_prediction",
                    "id": f"conflict_{int(datetime.now().timestamp())}",
                    "risk_score": risk,
                    "affected_agents": affected,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "status": "active"
                })
                print(f"⚠️  Conflict Predicted: Risk {risk:.2f} agents {affected}")

        except Exception as e:
            print(f"❌ Simulation Error: {e}")

@app.on_event("startup")
async def start_simulation_task():
    asyncio.create_task(simulate_system_activity())

if __name__ == "__main__":
    print("Starting Demo Backend on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
