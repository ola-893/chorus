# Chorus Agent Conflict Predictor

A real-time conflict prediction and intervention system for decentralized multi-agent networks using Google's Gemini 3 Pro API for game theory analysis.

## Project Structure

```
backend/
├── src/                           # Source code
│   ├── prediction_engine/         # Core prediction engine
│   │   ├── models/               # Data models and types
│   │   ├── game_theory/          # Game theory analysis components
│   │   └── interfaces.py         # Base interfaces for all components
│   ├── integrations/             # External service integrations
│   ├── api/                      # FastAPI REST endpoints
│   ├── config.py                 # Configuration management
│   └── logging_config.py         # Logging setup
├── tests/                        # Test suite
├── requirements.txt              # Python dependencies
├── pytest.ini                   # Pytest configuration
├── conftest.py                   # Pytest fixtures
├── setup.py                      # Package setup
├── setup_env.sh                  # Environment setup script
└── .env.example                  # Example environment configuration
```

## Quick Start

1. **Set up the environment:**
   ```bash
   ./setup_env.sh
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

5. **Check code coverage:**
   ```bash
   pytest --cov=src
   ```

## Core Components

### Interfaces
- **Agent**: Base interface for autonomous agents
- **GeminiClient**: Interface for Google Gemini API integration
- **TrustManager**: Interface for managing agent trust scores
- **InterventionEngine**: Interface for quarantine and intervention logic
- **ResourceManager**: Interface for shared resource management
- **AgentNetwork**: Interface for agent simulation orchestration

### Data Models
- **AgentIntention**: Represents an agent's intention to perform an action
- **ConflictAnalysis**: Result of game theory conflict analysis
- **TrustScoreEntry**: Trust score record for agents
- **QuarantineAction**: Record of quarantine interventions
- **ResourceRequest**: Request for shared resources

## Configuration

The system uses environment variables for configuration. Key settings include:

- `GEMINI_API_KEY`: Google Gemini API key (required)
- `REDIS_HOST`: Redis server host for trust score storage
- `MIN_AGENTS`/`MAX_AGENTS`: Agent simulation parameters
- `TRUST_SCORE_THRESHOLD`: Quarantine threshold (default: 30)
- `CONFLICT_RISK_THRESHOLD`: Intervention threshold (default: 0.7)

## Testing

The project uses pytest with the following test categories:

- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Integration Tests**: Tests with real external services (marked with `@pytest.mark.integration`)
- **Property Tests**: Property-based tests using Hypothesis

Run specific test categories:
```bash
pytest -m "not integration"  # Unit tests only
pytest -m integration        # Integration tests only
pytest -m property          # Property-based tests only
```

## Development

### Code Quality
- **Black**: Code formatting (`black src tests`)
- **Flake8**: Linting (`flake8 src tests`)
- **MyPy**: Type checking (`mypy src`)

### Coverage Requirements
- Minimum 80% overall coverage
- 95%+ coverage for critical paths (conflict prediction, trust scoring, quarantine logic)

## Architecture

The system follows a layered architecture with clear separation of concerns:

1. **CLI Dashboard Layer**: Real-time monitoring interface
2. **Intervention Engine**: Quarantine and intervention logic
3. **Conflict Predictor & Trust Manager**: Core prediction and scoring
4. **Gemini Client & Redis Client**: External service interfaces
5. **Agent Simulator**: Synthetic multi-agent environment

## System Status

The Chorus Agent Conflict Predictor is **fully implemented and ready for production deployment**. All core components are complete:

✅ **Gemini API Integration** - Game theory conflict analysis using Google's Gemini 3 Pro API  
✅ **Redis Trust Management** - Persistent trust scoring and quarantine management  
✅ **Agent Simulation** - Multi-agent environment with autonomous behavior  
✅ **Intervention Engine** - Automated quarantine and conflict prevention  
✅ **CLI Dashboard** - Real-time monitoring and system visualization  
✅ **REST API** - FastAPI-based endpoints for external integration  
✅ **Observability** - Comprehensive logging, health checks, and Datadog integration  
✅ **Deployment** - Docker, Kubernetes, and native Linux deployment options  

## Deployment

The system is ready for production deployment with multiple options:

### Quick Start (Docker)
```bash
# Development
./deploy-docker.sh dev

# Production
./deploy-docker.sh prod

# Validate deployment
./validate-deployment.sh
```

### Production Deployment
```bash
# Linux production deployment
sudo ./deploy.sh deploy

# Kubernetes deployment
kubectl apply -f k8s-deployment.yml
```

See the comprehensive deployment documentation:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
- [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md) - Quick start instructions
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre-deployment checklist
- [DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md) - System readiness report
- [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md) - Configuration reference
- [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md) - Troubleshooting guide