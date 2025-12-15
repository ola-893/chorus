# Chorus Multi-Agent Immune System - Comprehensive Demo

Welcome to the comprehensive demonstration of the Chorus Multi-Agent Immune System! This demo showcases a real-time safety layer for decentralized multi-agent systems that predicts and prevents emergent failures before they cascade.

## 🎯 What is Chorus?

Chorus is an innovative AI-powered immune system for multi-agent networks that:

- **Predicts Conflicts**: Uses Google Gemini 3 Pro AI to analyze agent interactions and predict potential conflicts before they occur
- **Manages Trust**: Maintains dynamic trust scores for all agents and automatically quarantines suspicious actors
- **Prevents Cascading Failures**: Implements real-time intervention mechanisms to isolate problematic agents
- **Provides Observability**: Offers comprehensive monitoring through CLI dashboards and REST APIs
- **Integrates Seamlessly**: Works with Redis, Datadog, ElevenLabs, and other enterprise services

## 🚀 Quick Start

### Option 1: Full Frontend Demo (Recommended)

```bash
./run_frontend_demo.sh
```

This launches the complete system with:
- Backend API with real-time data simulation
- React frontend dashboard with live updates
- WebSocket communication for real-time events
- Interactive agent monitoring and system health

### Option 2: Interactive Demo Menu

```bash
./demo_scenarios.sh
```

This launches an interactive menu with all demo options and automatic prerequisite checking.

### Option 3: Backend-Only Demos

```bash
# Full system demonstration (10 minutes)
python comprehensive_demo.py --mode full

# Quick simulation demo (5 minutes)
python comprehensive_demo.py --mode simulation

# CLI Dashboard demo (3 minutes)
python comprehensive_demo.py --mode dashboard
```

### Option 4: Individual Component Demos

```bash
# CLI Dashboard
cd backend && python demo_cli_dashboard.py

# Conflict Prediction
cd backend && python demo_intervention.py

# Agent Simulation
cd backend && python demo_simulation.py
```

## 📋 Prerequisites

### Required
- **Python 3.9+**: Core runtime environment
- **Redis Server**: For persistent trust score storage
- **Gemini API Key**: For AI-powered conflict prediction

### Optional (for full functionality)
- **Datadog API Keys**: For observability and monitoring
- **ElevenLabs API Key**: For voice alerts
- **Docker**: For containerized deployment
- **Node.js 18+**: For React dashboard

### Environment Setup

1. **Copy environment configuration:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Edit configuration with your API keys:**
   ```bash
   # Required
   CHORUS_GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional but recommended
   CHORUS_DATADOG_API_KEY=your_datadog_api_key
   CHORUS_ELEVENLABS_API_KEY=your_elevenlabs_key
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Start Redis:**
   ```bash
   redis-server  # Or use Docker: docker run -d -p 6379:6379 redis
   ```

## 🎬 Demo Scenarios

### 1. Full Frontend Demo (15 minutes)
**Recommended for first-time viewers - Complete visual experience**

```bash
./run_frontend_demo.sh
```

**What you'll see:**
- 🌐 **Modern React Dashboard**: Beautiful, responsive web interface
- 📊 **Real-time Agent Monitoring**: Live agent cards with trust scores, status, and resource usage
- ⚡ **WebSocket Updates**: Instant updates as agents interact and trust scores change
- 🎯 **Interactive Elements**: Click agents for detailed history, filter and sort options
- 🔮 **Live Conflict Prediction**: Real-time AI analysis with risk assessment
- 🚫 **Quarantine Visualization**: Watch agents get quarantined in real-time
- 📈 **System Health Dashboard**: Live metrics, dependencies, and circuit breakers
- 🎨 **Cyberpunk Aesthetics**: Glowing effects, animations, and modern UI design

### 2. Backend System Demo (10 minutes)
**Focus on core system capabilities**

```bash
python comprehensive_demo.py --mode full
```

**What you'll see:**
- ✅ System health monitoring and component status
- 🤖 Multi-agent simulation with 6 autonomous agents
- 🔮 AI-powered conflict prediction using Gemini 3 Pro
- 🛡️ Dynamic trust scoring and management
- 🚫 Real-time intervention and quarantine mechanisms
- 📊 Live CLI dashboard with metrics visualization
- 🌐 REST API integration demonstration
- 🔌 External service integrations (Redis, Datadog, etc.)

### 2. Agent Simulation Demo (5 minutes)
**Focus on core agent behavior and conflict prediction**

```bash
python comprehensive_demo.py --mode simulation
```

**What you'll see:**
- 🤖 Agent creation and lifecycle management
- 💬 Inter-agent communication simulation
- 🔄 Resource contention scenarios
- 🔮 Real-time conflict analysis with Gemini AI
- 📈 Risk assessment and prediction outcomes

### 3. Interactive CLI Dashboard (Continuous)
**Real-time monitoring interface**

```bash
cd backend
python demo_cli_dashboard.py --agents 8
```

**Features:**
- 📊 Real-time system metrics with color-coded status
- 🤖 Live agent status and trust scores
- ⚡ Resource utilization monitoring (CPU, Memory, Network, Storage)
- 🔮 Conflict prediction with risk levels
- 🚫 Intervention tracking and history
- 🎯 Visual progress bars and status indicators

### 4. Conflict Prediction Demo
**Deep dive into AI-powered analysis**

```bash
cd backend
python demo_intervention.py
```

**Demonstrates:**
- 🧠 Gemini 3 Pro integration for game theory analysis
- 📊 Multi-scenario conflict prediction
- 🎯 Risk scoring and threshold management
- 🚫 Automated intervention triggers
- 📝 Detailed analysis logging

### 5. API Integration Demo (2 minutes)
**REST API and service integration**

```bash
python comprehensive_demo.py --mode api
```

**API Endpoints Demonstrated:**
- `GET /health` - System health status
- `GET /agents` - Agent listing and status
- `GET /agents/{id}/trust-score` - Individual trust scores
- `POST /agents/{id}/quarantine` - Manual quarantine
- `GET /conflicts/predict` - Conflict prediction
- `GET /dashboard/metrics` - Real-time metrics

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chorus Immune System                     │
├─────────────────────────────────────────────────────────────┤
│  CLI Dashboard  │  REST API  │  Web Dashboard (Optional)    │
├─────────────────────────────────────────────────────────────┤
│              Intervention Engine                            │
│         (Quarantine & Safety Mechanisms)                   │
├─────────────────────────────────────────────────────────────┤
│  Conflict Predictor  │  Trust Manager  │  Agent Simulator  │
│   (Gemini 3 Pro)    │   (Redis Store) │  (Multi-Agent)    │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                      │
│  Redis │ Datadog │ ElevenLabs │ Confluent (Future)         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Development & Testing

### Run Test Suite
```bash
cd backend

# Unit tests only
pytest -m "not integration"

# Integration tests (requires external services)
pytest -m integration

# Property-based tests
pytest -m property

# All tests with coverage
pytest --cov=src --cov-report=html
```

### Development Environment
```bash
# Start backend API server
cd backend
python src/main.py

# Start frontend dashboard (if available)
cd frontend
npm start

# Or use the interactive menu
./demo_scenarios.sh
# Choose option 11: Start Development Environment
```

### Docker Deployment
```bash
# Development environment
docker-compose up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d

# Or use the deployment script
./backend/deploy-docker.sh dev
```

## 📊 Demo Metrics & Statistics

During the demo, you'll see real-time statistics including:

- **Agents Created**: Number of autonomous agents in the simulation
- **Conflicts Predicted**: AI-powered conflict analyses performed
- **Interventions Performed**: Quarantine and safety actions taken
- **Trust Scores Updated**: Dynamic trust score modifications
- **API Calls Made**: External service interactions

## 🎯 Key Demo Highlights

### 1. AI-Powered Conflict Prediction
Watch as Gemini 3 Pro analyzes agent interactions in real-time:
```
🔮 Analyzing: Resource Contention
   Agents: agent_001, agent_002, agent_003
   Result: 🔴 HIGH RISK (78.2%)
   Prediction: Cascading failure due to resource deadlock
   Recommendations: isolate_agents, redistribute_resources
```

### 2. Dynamic Trust Management
See trust scores change based on agent behavior:
```
Trust Score Updates:
  ⬆️ agent_001: +10 (successful cooperation) → 85
  ⬇️ agent_002: -25 (resource hoarding) → 45
  ⬇️ agent_003: -40 (suspicious activity) → 15 ⚠️
```

### 3. Real-Time Intervention
Watch the system automatically quarantine problematic agents:
```
🚫 Quarantining agent_003 (trust score: 15)
   ✅ Quarantine successful
   🔒 Agent isolated from network
   📝 Intervention logged
```

### 4. Live Dashboard Monitoring
Experience the real-time CLI dashboard:
```
CHORUS AGENT CONFLICT PREDICTOR - DASHBOARD
================================================================================
SYSTEM STATUS: 🟢 RUNNING | Gemini API: 🟢 CONNECTED
AGENT STATUS: Total: 8 | Active: 6 | Quarantined: 2
RESOURCE UTILIZATION:
  cpu    : [███████████████░░░░░] 75.0% 🟡
  memory : [████████████░░░░░░░░] 60.0% 🟢
CONFLICT PREDICTION: [█████████████░░░░░░░] 65.0% 🟡 MODERATE RISK
```

## 4. Frontend Dashboard Demo (Real-Time Visuals)

Experience the full power of the Chorus Immune System with our Cyberpunk-themed React dashboard.

### **Features**
*   **Real-Time Visualization:** Watch trust scores update live via WebSockets.
*   **Visual Feedback:** Agents flash red when quarantined, green when active.
*   **System Health:** Live monitoring of backend components and uptime.
*   **Cyberpunk UI:** Modern, responsive interface with animations.

### **How to Run**
Simply execute the all-in-one script:
```bash
./run_frontend_demo.sh
```
This will:
1.  Start the backend simulation engine (generating fake agent traffic).
2.  Launch the React frontend.
3.  Open the dashboard in your default browser.

### **What to Watch For**
*   **Trust Scores:** Agents randomly gain or lose trust based on simulated interactions.
*   **Quarantine:** If an agent's score drops below 30, it gets quarantined immediately.
*   **Conflict Alerts:** Occasional high-risk conflict predictions will appear.

---
## 5. Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Start Redis server
   redis-server
   
   # Or use Docker
   docker run -d -p 6379:6379 redis
   ```

2. **Gemini API Key Invalid**
   ```bash
   # Check your .env file
   cat backend/.env | grep GEMINI_API_KEY
   
   # Verify API key at: https://makersuite.google.com/app/apikey
   ```

3. **Python Dependencies Missing**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Permission Errors (Linux/Mac)**
   ```bash
   chmod +x demo_scenarios.sh
   chmod +x backend/deploy.sh
   ```

### Debug Mode

Enable detailed logging for troubleshooting:
```bash
python comprehensive_demo.py --mode full --debug
```

### Health Check

Verify system components:
```bash
cd backend
python -c "
from src.system_health import SystemHealthChecker
import asyncio
asyncio.run(SystemHealthChecker().check_all_components())
"
```

## 🌟 What Makes This Demo Special

### 1. **Real AI Integration**
- Uses actual Google Gemini 3 Pro API for conflict prediction
- Demonstrates practical AI application in system safety
- Shows game theory analysis in action

### 2. **Production-Ready Architecture**
- Follows enterprise software patterns
- Includes comprehensive error handling
- Implements proper logging and monitoring

### 3. **Multi-Modal Interfaces**
- CLI dashboard for real-time monitoring
- REST API for programmatic access
- Web dashboard for user-friendly interaction

### 4. **Comprehensive Testing**
- Unit tests with 80%+ coverage
- Integration tests with real services
- Property-based testing for correctness

### 5. **Enterprise Integrations**
- Redis for persistent storage
- Datadog for observability
- ElevenLabs for voice alerts
- Docker for containerization

## 📚 Additional Resources

- **[Backend README](backend/README.md)**: Detailed technical documentation
- **[Deployment Guide](backend/DEPLOYMENT.md)**: Production deployment instructions
- **[CLI Dashboard Guide](backend/CLI_DASHBOARD_README.md)**: Dashboard usage and features
- **[API Documentation](backend/src/api/main.py)**: REST API endpoints and schemas

## 🎉 Next Steps

After running the demo:

1. **Explore the Code**: Browse the well-documented source code
2. **Run Tests**: Execute the comprehensive test suite
3. **Customize Configuration**: Modify settings for your use case
4. **Deploy to Production**: Use the provided deployment scripts
5. **Integrate with Your Systems**: Adapt the APIs for your infrastructure

## 🤝 Contributing

This demo showcases a production-ready system built with:
- **Clean Architecture**: Modular, testable, maintainable code
- **Industry Standards**: Following best practices for enterprise software
- **Comprehensive Documentation**: Clear guides and examples
- **Robust Testing**: Multiple testing strategies for reliability

Ready to see the future of multi-agent system safety? Run the demo and experience Chorus in action!

```bash
./demo_scenarios.sh
```

---

**Chorus Multi-Agent Immune System** - Preventing cascading failures in decentralized AI systems through predictive intervention and real-time trust management.