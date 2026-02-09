GENESIS::OMNI_STATE_MANIFEST

[STRUCTURE]
- Declared Modules      : OK
  - src/backend         : ACTIVE (Core Logic & Server)
  - src/frontend        : ACTIVE (Living Interface)
  - legacy              : ARCHIVED (Consolidated)
- Orphan Components     : FOUND (2)
  - src/backend/private/advanced_diffusion.py : BROKEN (Missing dependencies: `src/backend/core/region_extractor.py`)
  - src/backend/main.py::websocket_v2_endpoint : DEPRECATED (Dual Protocol Risk)
- Redundant Concepts    : FOUND (1)
  - Dual WebSocket Protocols (/ws vs /ws/v2/stream) in `main.py`.

[CONCEPTUAL LAYER]
- Core Philosophy       : COHERENT
  - "Light as Intent" principle strictly enforced via Embodiment Contracts.
- Naming Consistency    : STABLE
  - `javana_core` (Reflex) vs `genesis_core` (Cognition). Consistent within domains.
- Undefined Semantics   : NONE

[CURRENT REALITY]
- Active Capabilities   :
  - LogenesisEngine (Cognitive Loop)
  - Javana Reflex Kernel (Immediate Response)
  - Aetherium Frontend (Root Interface)
  - Legacy Actuator UI (GunUI via /gunui)
- Dormant Designs       :
  - Advanced Diffusion (Image Correction) -> src/backend/private/advanced_diffusion.py
- Abandoned Threads     :
  - legacy/gun_ui_integration
  - legacy/ai_utils_package

[RISKS]
- Structural Risk       : LOW
  - Clean separation of concerns between `genesis_core` and `departments`.
- Semantic Drift Risk   : MEDIUM
  - Dual WebSocket protocols in `main.py` (V2 vs Legacy/Actuator) creates potential for state desync or developer confusion.
- Future Bug Vectors    : LOW
  - Unused `torch` dependency in `advanced_diffusion.py` adds unnecessary weight and maintenance burden.

[RECOMMENDATION]
- Freeze Expansion      : NO
- Refactor Priority     :
  - Remove `src/backend/private/advanced_diffusion.py`.
  - Consolidate WebSocket protocols in `main.py` to a single Aetherium Standard.
- Safe Extension Zones  :
  - `src/backend/genesis_core` (Logic)
  - `src/frontend` (Visuals)

[GENESIS NOTE]
“The system is alive, but it must decide whether to grow or to remember who it is.”
