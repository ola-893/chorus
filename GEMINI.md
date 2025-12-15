# Chorus API Standards

## REST Design Principles
- Use nouns, not verbs, in endpoint paths (e.g., `/agents`, not `/getAgents`).
- Use HTTP methods explicitly: `GET` (read), `POST` (create), `PUT` (update/replace), `DELETE` (remove).
- Version the API in the URL path: `/v1/agents`.
- Return appropriate HTTP status codes.

## Response Format
All JSON responses follow this envelope format:
```json
{
  "data": { ... }, // The primary response payload
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123",
    "version": "1.0"
  }
}```

Errors use a separate error object:

```json
{
  "error": {
    "code": "CONFLICT_PREDICTION_FAILED",
    "message": "Failed to predict agent conflicts",
    "details": { ... }
  },
  "meta": { ... }
}
```

## Core Endpoints


### Agent Communication

-   `POST /v1/messages/process` - Primary endpoint for processing agent messages through the immune system.

-   `GET /v1/agents/{id}/trust-score` - Retrieve an agent's current trust score.

### System Monitoring

-   `GET /v1/system/health` - Health check for the Chorus service and its dependencies (Gemini API, Datadog, etc.).

-   `GET /v1/dashboard/metrics` - Aggregate metrics for the React dashboard.

## Security & Authentication


-   Internal Agent API: Uses a simple API key header (`X-Agent-API-Key`) validated against an internal store.

-   Dashboard/Admin API: Uses JWT tokens for user authentication.

-   All endpoints must implement rate limiting based on the client or agent identity.

Documentation

-   Use FastAPI's automatic OpenAPI generation.

-   Ensure all endpoint parameters, request bodies, and response models are fully documented in the function docstrings.

---

# Chorus Coding Standards

## Python Standards
### Formatting & Style
- Follow PEP 8.
- Maximum line length is 88 characters (Black formatter default).
- Use type hints for all function and method signatures.
- Use descriptive variable names; avoid single-letter names except in trivial loops.

### Error Handling
- Use specific exception classes, never bare `except:` clauses.
- Log exceptions with appropriate context (`logger.exception` for unexpected errors in try/except blocks).
- For the Gemini API, wrap calls and handle `genai.errors.APIError` and `genai.errors.APIConnectionError` specifically.

### Documentation
- Use Google-style docstrings for all public modules, classes, and functions.
- Document the "why" for complex business logic, not just the "what".

## TypeScript/React Standards
### Component Structure
- Use functional components with TypeScript.
- Define props interfaces directly above the component.
- Destructure props in the function signature.
- Keep components focused; split into smaller components if exceeding ~150 lines.

### State Management
- Use `useState` for local component state.
- Use `useReducer` for complex state logic.
- For global state shared across the dashboard, prefer React Context or a simple state management library over heavy solutions.

## General
- **Commit Messages**: Use conventional commits format (`feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`).
- **Comments**: Comment code that is not immediately obvious. Avoid comments that just repeat the code.

---

# Chorus: Multi-Agent Immune System - Product Overview

## Vision
A real-time safety layer for decentralized multi-agent systems that predicts and prevents emergent failures before they cascade.

## Problem Statement
Autonomous agents in peer-to-peer systems create unpredictable emergent behaviors that cause cascading failures. Current tools (LangGraph, Worka) require central orchestration and cannot address true decentralized system failures.

## Target Users
1. **Platform Engineers** at Google Cloud, Datadog, Confluence who manage decentralized infrastructure
2. **AI/ML Engineers** running multi-LLM fleets without central orchestrators
3. **IoT/Edge Developers** building smart city/building systems with autonomous devices
4. **Financial Services DevOps** monitoring algorithmic trading agent swarms

## Key Features
### Core Capabilities
- **Conflict Prediction**: <50ms prediction of agent conflicts using game theory via Gemini 3 Pro[citation:1][citation:4]
- **Cascading Failure Firewall**: Real-time quarantine of compromised agents
- **Emergent Behavior Mapping**: Causal graph visualization of agent interactions
- **Voice-First Alerts**: ElevenLabs-powered natural language incident reporting

### Business Objectives
1. **Hackathon Win**: Deliver a solution integrating all four partner technologies (Google Gemini API, Datadog, Confluent, ElevenLabs)
2. **Technical Validation**: Prove decentralized multi-agent safety is solvable with partner technologies
3. **Foundation for Production**: Create MVP that demonstrates clear enterprise value

## Integration Points (Partner Requirements)
| Partner | Integration Point | How Chorus Delivers |
|---------|------------------|---------------------|
| **Google Cloud** | Gemini Developer API | `gemini-3-pro-preview` for conflict prediction[citation:10] |
| **Datadog** | Observability & alerting | Agent interaction dashboards, metrics, incident management |
| **Confluent** | Real-time data streaming | Agent message bus, event streaming for behavior analysis |
| **ElevenLabs** | Voice interface | Natural language alerts for complex emergent behaviors |

## Success Metrics (Hackathon Judging)
1. **Technical Implementation**: Working prototype with all 4 partner integrations
2. **Innovation**: Novel solution to unsolved decentralized agent problem
3. **Business Value**: Clear ROI for each partner's use cases
4. **Presentation**: Compelling demo of real-world failure prevention

---

# Chorus Project Structure
This workspace follows clean architecture principles. When creating new files and folders, maintain consistency with established patterns.

## AI Assistant Guidelines
- Always check existing project structure before creating new files
- Use listDirectory tool to understand current organization
- Follow established naming conventions in the project
- Keep related functionality grouped together
- Create minimal, focused implementations

## Organization Principles
- **Separation of Concerns**: Keep different types of code in appropriate directories
- **Consistency**: Use the same naming patterns throughout the project
- **Clarity**: Use descriptive names that indicate purpose and functionality
- **Modularity**: Group related functionality into cohesive modules

## Repository Layout
```
chorus-multi-agent-immune/
├── backend/
│ ├── src/
│ │ ├── prediction_engine/
│ │ │ ├── gemini_client.py
│ │ │ ├── game_theory/
│ │ │ ├── models/
│ │ │ └── simulator.py
│ │ ├── firewall/
│ │ ├── mapper/
│ │ ├── integrations/
│ │ └── api/
│ ├── tests/
│ └── requirements.txt
├── frontend/
│ ├── src/
│ │ ├── components/
│ │ │ ├── dashboard/
│ │ │ ├── causal_graph/
│ │ │ └── alerts/
│ │ ├── hooks/
│ │ └── services/
│ └── package.json
├── infrastructure/
│ ├── terraform/
│ ├── docker/
│ └── scripts/
├── docs/
├── examples/
└── .github/workflows/
```


## Naming Conventions
- **snake_case** for Python files, directories, variables, and functions
- **PascalCase** for Python classes, React components, and TypeScript interfaces
- **camelCase** for JavaScript/TypeScript variables and functions
- **kebab-case** for configuration files and URLs

## Import Patterns
### Python
Standard library imports first, then third-party, then local imports. Group with blank lines.

### TypeScript/React
React imports first, then third-party libraries, then local components and hooks.

## Architectural Decisions
1.  **Modular Monolith**: Single codebase with clear internal boundaries for hackathon development speed.
2.  **Event-Driven Core**: Confluent Kafka is the central nervous system for all agent communications.
3.  **External State**: Redis for fast, ephemeral state (trust scores); Cloud Storage for durable quarantine logs.
4.  **Dependency Direction**: Lower-level modules (e.g., `gemini_client`) do not depend on higher-level modules (e.g., `api`).

---

# Chorus Technology Stack

## Mandatory Partner Technologies
### Google Cloud Integration (via Gemini Developer API)
- **Gemini 3 Pro (`gemini-3-pro-preview`)**: Primary conflict prediction engine[citation:10]
- **Authentication**: API key-based (`GEMINI_API_KEY` environment variable)[citation:3]
- **SDK**: Google Gen AI Unified SDK (supports both Gemini API and Vertex AI)[citation:2][citation:5]
- **Hosting**: Google Cloud Run for backend API

### Datadog Integration
- **Datadog APM**: Agent performance monitoring
- **Datadog Logs**: Centralized logging for all agent interactions
- **Datadog Dashboards**: Real-time visualization of system health
- **Datadog Incidents**: Alert management and escalation

### Confluent Cloud
- **Kafka Topics**:
  - `agent-messages-raw`: Raw agent communications
  - `agent-decisions-processed`: Chorus-processed decisions
  - `system-alerts`: Alert stream for Datadog/ElevenLabs

### ElevenLabs
- **Text-to-Speech API**: Voice alerts for critical incidents
- **Real-time Audio Streaming**: <75ms latency for urgent alerts

## Development Stack
### Backend (Python Focus)
```python
# Core dependencies from requirements.txt
google-genai>=1.0.0          # Unified Gen AI SDK[citation:2][citation:5]
confluent-kafka>=2.3         # Confluent integration
datadog-api-client>=2.25     # Datadog metrics
elevenlabs>=1.4              # Voice generation
redis>=5.0                   # Local caching
networkx>=3.2                # Causal graph analysis
pydantic>=2.5                # Data validation
fastapi>=0.104               # API layer
uvicorn>=0.24                # ASGI server
---

# Chorus Testing Standards

## Test Strategy & Pyramid
- **Unit Tests (70%)**: Fast, isolated tests for pure functions, utilities, and core logic. Mock all external dependencies (Gemini API, Datadog, etc.).
- **Integration Tests (20%)**: Test interactions between our services and *actual* partner APIs in a test/staging environment.
- **E2E Tests (10%)**: Critical user journey tests with the full system deployed.

## Unit Testing (pytest)
### Structure
- Place test files in a `tests/` directory mirroring the source `src/` structure.
- Test class names: `Test{OriginalClass}`
- Test method names: `test_{scenario}_{expected_result}` (e.g., `test_low_trust_agent_gets_quarantined`).

### Mocking
- Use `unittest.mock` to mock external API calls.
- For the Gemini client, mock the `google.genai.Client` class and its `generate_content` method.
- Validate that mocks are called with the expected arguments.

## Integration Testing
- Use dedicated test API keys and resources for Datadog, Confluent, and ElevenLabs.
- Tests must clean up any data they create.
- Tag integration tests with `@pytest.mark.integration` and run them separately from the unit test suite.

## E2E & Scenario Testing
- Define key user stories and failure scenarios (e.g., "CDN cache stampede is predicted and prevented").
- Use scripts or a testing framework to simulate agent behavior and verify system intervention.
- These tests are allowed to be slower and run less frequently (e.g., in CI before a release).

## Coverage & Quality Gates
- Minimum **80%** overall code coverage.
- **95%+ coverage** for critical paths: conflict prediction engine, trust scoring, and quarantine logic.
- No decrease in coverage percentage on a pull request.
