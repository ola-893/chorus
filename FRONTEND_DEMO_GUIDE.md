# 🎭 Chorus Frontend Demo Guide

Welcome to the Chorus Multi-Agent Immune System visualization. This dashboard provides a real-time window into the conflict prediction and trust management engine.

## 🚀 Quick Start

```bash
./run_frontend_demo.sh
```

This single command launches the entire stack:
1.  **Backend (Port 8000):** Starts the API and the Simulation Engine.
2.  **Frontend (Port 3000):** Starts the React development server.

## 🖥️ Dashboard Interface

### 1. System Health (Top Panel)
*   **Overall Status:** Indicates if the backend prediction engine is running.
*   **Uptime:** Seconds since the system started.
*   **Component Status:** Live check of dependencies (Redis, Gemini API, Config).

### 2. Agent Monitor (Main Grid)
The grid displays all active agents in the network.

*   **Active Agents (Green Border):**
    *   Trust Score > 30.
    *   Operating normally.
*   **Quarantined Agents (Red Border + Background):**
    *   Trust Score < 30.
    *   Isolated from the network to prevent cascade failures.
    *   **Animation:** Shake effect on score drop.

### 3. Real-Time Metrics
*   **Trust Score:** Updated instantly via WebSocket when the backend simulation generates an event.
*   **Updates:** "Updated: [Time]" timestamp shows the freshness of the data.

## 🔧 Technical Underpinnings

### Data Flow
1.  **Simulation (`backend/frontend_demo.py`):** Randomly adjusts trust scores and generates conflict risks.
2.  **Event Bus (`backend/src/event_bus.py`):** Decouples the simulation from the API.
3.  **WebSocket (`backend/src/api/main.py`):** Broadcasts events from the bus to all connected clients.
4.  **React Client (`frontend/src/services/api.ts`):** Listens for events and updates component state.

### Key Technologies
*   **FastAPI & Uvicorn:** Async Python backend.
*   **React & TypeScript:** Type-safe frontend.
*   **WebSockets:** Full-duplex communication for sub-millisecond updates.
*   **CSS Variables:** Theming engine for the Cyberpunk look.

## ❓ Troubleshooting

**"WebSocket Disconnected" in Console:**
*   Ensure the backend is running (`python3 backend/frontend_demo.py`).
*   Check if port 8000 is blocked.

**No Agents Appearing:**
*   The simulation takes 1-2 seconds to generate initial data.
*   Check the terminal output of `run_frontend_demo.sh` for "Simulation Error".

**Styles Look Wrong:**
*   Ensure your browser supports CSS Variables (modern browsers only).
