# 📖 AETHERIUM GENESIS User Guide

Aetherium Genesis is designed as a **Web-Native Platform** accessible through multiple channels, each serving a specific purpose.

---

## 1. Web Interface (Desktop & Development)
This is the primary channel for development and testing, accessible via a web browser.

### How to Run
**Method 1: The Ritual Script (Recommended)**
This script performs a system integrity check, purges stale memory segments, and launches the core automatically.
```bash
python awaken.py
```

**Method 2: Direct Core Backend Launch**
Use this if you need to manually configure ports or reload options.
```bash
export PYTHONPATH=$PYTHONPATH:.
python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points
*   **Product Interface:** [http://localhost:8000](http://localhost:8000)
    *   The main interface for end-users (The Living Interface).
    *   Displays the particle system and emotional responses.
*   **Developer Dashboard:** [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
    *   A control center for developers to view logs, memory state, and manipulate variables.

---


## 3. API & Connectivity
For developers wishing to connect directly to the system's "Cognitive Core".

*   **WebSocket Endpoint:** `ws://localhost:8000/ws` and `ws://localhost:8000/ws/v3/stream`
    *   Used for sending text input and receiving real-time state/visuals.
*   **Health Check Protocol:** The system broadcasts health metrics (Heartbeat) via the AetherBus, which can be monitored through the same WebSocket connection.
