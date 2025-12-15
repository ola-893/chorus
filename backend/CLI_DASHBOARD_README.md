# CLI Dashboard - Chorus Agent Conflict Predictor

## Overview

The CLI Dashboard provides real-time monitoring of the Chorus Agent Conflict Predictor system through a terminal-based interface. It displays agent status, system metrics, conflict predictions, and intervention actions without requiring user input.

## Features

### System Status
- ✅ System running status (RUNNING/STOPPED)
- ✅ Gemini API connection status (CONNECTED/DISCONNECTED)
- ✅ Configuration thresholds display

### Agent Monitoring
- ✅ Total, active, and quarantined agent counts
- ✅ Individual agent trust scores with visual indicators
- ✅ Trust score threshold warnings (⚠️ for scores below 30)

### Resource Utilization
- ✅ Visual progress bars for CPU, Memory, Network, Storage, Database
- ✅ Color-coded status indicators:
  - 🟢 Green: < 60% utilization
  - 🟡 Yellow: 60-80% utilization  
  - 🔴 Red: > 80% utilization

### Conflict Prediction
- ✅ Real-time conflict risk score with visual bar
- ✅ Risk level indicators (LOW/MODERATE/HIGH RISK)
- ✅ Recent conflict predictions history
- ✅ Affected agents display
- ✅ Predicted failure modes for high-risk scenarios

### Intervention Tracking
- ✅ Recent intervention actions with timestamps
- ✅ Action types (QUARANTINE, etc.) with icons
- ✅ Target agents and confidence levels
- ✅ Detailed intervention reasons

## Usage

### Basic Usage
```bash
# Start with default settings
python cli_dashboard.py

# Start with specific number of agents
python cli_dashboard.py --agents 7

# Enable debug logging
python cli_dashboard.py --log-level DEBUG

# Custom refresh interval
python cli_dashboard.py --refresh-interval 1.0
```

### Demo Mode
```bash
# Run demo without external dependencies
python demo_cli_dashboard.py
```

### Command Line Options
- `--agents N`: Number of agents to create (5-10)
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--refresh-interval SECONDS`: Dashboard refresh interval (default: 2.0)
- `--no-clear`: Don't clear screen on startup (useful for debugging)

## Requirements

### Required Environment Variables
```bash
export GEMINI_API_KEY="your_gemini_api_key"  # For conflict prediction
```

### Optional Environment Variables
```bash
export REDIS_HOST="localhost"                # Redis server host
export REDIS_PORT="6379"                    # Redis server port
export CONFLICT_RISK_THRESHOLD="0.7"        # Risk threshold for interventions
export TRUST_SCORE_THRESHOLD="30"           # Trust score quarantine threshold
```

### External Dependencies
- **Redis Server**: Required for trust score persistence
- **Gemini API**: Required for conflict prediction (falls back gracefully if unavailable)

## Display Layout

```
CHORUS AGENT CONFLICT PREDICTOR - DASHBOARD
                                                Last Update: 2025-12-14 17:22:07
================================================================================
SYSTEM STATUS:
  Status: 🟢 RUNNING
  Gemini API: 🟢 CONNECTED
  Conflict Risk Threshold: 0.7
  Trust Score Threshold: 30
--------------------------------------------------------------------------------
AGENT STATUS:
  Total Agents: 8
  Active Agents: 6
  Quarantined Agents: 2
  Trust Scores:
    agent_006:  15 ⚠️
    agent_003:  25 ⚠️
    agent_004:  78 ✅
--------------------------------------------------------------------------------
RESOURCE UTILIZATION:
  cpu         : [███████████████░░░░░]  75.0% 🟡
  memory      : [████████████░░░░░░░░]  60.0% 🟢
  database    : [█████████████████░░░]  85.0% 🔴
--------------------------------------------------------------------------------
CONFLICT PREDICTION:
  Current Risk: [█████████████░░░░░░░]  65.0% 🟡 MODERATE
  Last Update: 15s ago
  Recent Predictions:
    17:22:05 🟡  65.1% - agent_001, agent_003, agent_006
    17:21:50 🔴  78.2% - agent_002, agent_004
      └─ Resource contention leading to cascading failure...
--------------------------------------------------------------------------------
RECENT INTERVENTIONS:
  Total: 3 | Quarantines: 2

  17:22:03 🚫 QUARANTINE  agent_006   (95%)
    └─ High conflict risk (0.782): Resource contention leading to...
  17:21:45 🚫 QUARANTINE  agent_003   (88%)
    └─ Trust score below threshold (25)
```

## Keyboard Controls

- **Ctrl+C**: Gracefully stop the dashboard and system
- The dashboard runs continuously without user input required

## Troubleshooting

### Common Issues

1. **Redis Connection Refused**
   ```
   Error 61 connecting to localhost:6379. Connection refused.
   ```
   - Start Redis server: `redis-server`
   - Or use demo mode: `python demo_cli_dashboard.py`

2. **Gemini API Unavailable**
   ```
   Gemini API: 🔴 DISCONNECTED
   ```
   - Set `GEMINI_API_KEY` environment variable
   - Check API key validity
   - System continues with limited functionality

3. **Terminal Display Issues**
   - Ensure terminal supports ANSI escape sequences
   - Use `--no-clear` flag for debugging
   - Minimum terminal size: 80x30 characters

### Logging

The dashboard logs to stdout with configurable levels:
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues (Redis/API failures)
- **ERROR**: Critical errors that don't stop operation
- **DEBUG**: Detailed operation information

## Integration

The CLI dashboard integrates with:
- **Agent Simulator**: Monitors agent behavior and status
- **Trust Manager**: Displays trust scores and quarantine status  
- **Intervention Engine**: Shows intervention actions and history
- **Gemini Client**: Performs real-time conflict prediction
- **Resource Manager**: Monitors resource utilization

## Architecture

```
CLIDashboard
├── DashboardMetrics (data collection)
├── Display Loop (real-time updates)
├── Conflict Prediction (Gemini integration)
└── System Integration (component coordination)
```

The dashboard operates independently of the core system and can be started/stopped without affecting agent simulation or conflict prediction functionality.