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

## Next Steps

This foundation provides the core interfaces and project structure. The next tasks involve implementing:

1. Gemini API integration for conflict analysis
2. Redis-based trust management system
3. Agent simulation environment
4. Intervention and quarantine logic
5. CLI dashboard for monitoring

See the tasks.md file in the spec directory for the complete implementation plan.