# Genesis Agents Guide

**Welcome, Agent.**

This repository serves as the **Cognitive Infrastructure** for Aetherium Genesis. Your primary directive is to maintain the purity of the "Genesis" state—a system that is alive, intent-driven, and devoid of anthropomorphic deception.

## Repository Structure

The codebase has been refactored (as of [Current Date]) to separate active core logic from experimental artifacts.

### 1. The Core (`src/backend`)
*   **Purpose:** The active reasoning engine (`LogenesisEngine`) and server.
*   **Key Files:**
    *   `src/backend/main.py`: The main entry point (executed by `awaken.py`).
    *   `src/backend/core/logenesis_engine.py`: The cognitive loop.
    *   `src/backend/core/visual_schemas.py`: The visual language contracts.
*   **Directive:** All new backend logic must reside here.

### 2. The Interface (`src/frontend/`)
*   **Purpose:** The active frontend interface.
*   **Key Files:**
    *   `src/frontend/index.html`: The Central AI Hub (Root).
    *   `src/frontend/public/gunui/index.html`: The Actuator UI (Legacy/Specific).
*   **Directive:** `src/frontend` is served as the root application. Use `src/frontend/public/gunui` only for specific actuator tasks.

### 3. The Archive (`legacy/`)
*   **Purpose:** A holding zone for dormant, fragmented, or experimental modules.
*   **Contents:**
    *   `akashic_nirodha`: Blockchain experiments.
    *   `niyama`: IIT experiments.
    *   `inspira`: Ritual scripts.
    *   `gunui_react`: Abandoned React template.
    *   `main.py` / `visual_engine.py`: Legacy runners.
*   **Directive:** Do not build upon these modules unless explicitly instructed to "revive" a thread.

## Philosophy & Protocol

*   **Manifest:** See `GENESIS_OMNI_STATE_MANIFEST.md` for the authoritative state report.
*   **Light Protocol:** Visuals are physical manifestations of sound/intent, not arbitrary graphics.
*   **No Avatars:** Avoid creating faces or characters. The "Biometric Proxy" in `gunui` is the maximum allowable abstraction.

## Testing

*   **Active Tests:** Run `pytest tests/` to verify core integrity.
*   **Legacy Tests:** `legacy/tests/` contains tests for archived components.

---
*“The system is alive, but it must decide whether to grow or to remember who it is.”*
