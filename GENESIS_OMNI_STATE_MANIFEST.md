GENESIS::OMNI_STATE_MANIFEST

[STRUCTURE]
- Declared Modules      : OK
  - src/backend         : ACTIVE (Core Logic & Server)
  - src/frontend        : ACTIVE (Living Interface)
- Orphan Components     : FOUND (1)
  - `tests/test_advanced_diffusion.py` removed because the corresponding source implementation is missing.
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
- Dormant Designs       : NONE
- Abandoned Threads     : CLEANED

[RISKS]
- Structural Risk       : LOW
  - Clean separation of concerns between `genesis_core` and `departments`.
- Semantic Drift Risk   : MEDIUM
  - Confirmed dual WebSocket protocol risk in `main.py` (`/ws` vs `/ws/v2/stream`) creates potential for state desync and developer confusion.
- Future Bug Vectors    : MEDIUM
  - Dependency on `google-generativeai` is deprecated and should be migrated to `google-genai`.

[TEST INTEGRITY]
- CI Status Alignment   : UPDATED
  - Removed unowned test `tests/test_advanced_diffusion.py` (source file missing).
  - Updated test imports to valid module paths:
    - `tests/test_lcl_physics.py` → `src.backend.genesis_core.models.light`
    - `tests/test_light_testbed.py` → `src.backend.main`
    - `tests/test_search_flow.py` → corrected `src.backend...` paths
  - Added `torch` mock guards in `tests/test_region_extractor.py` to skip safely when `conftest.py` mocks `torch`.

[RECOMMENDATION]
- Freeze Expansion      : NO
- Refactor Priority     :
  - Consolidate WebSocket protocols in `main.py` to a single Aetherium Standard.
  - Migrate from `google-generativeai` to `google-genai`.
- Safe Extension Zones  :
  - `src/backend/genesis_core` (Logic)
  - `src/frontend` (Visuals)

[GENESIS NOTE]
“The system is alive, but it must decide whether to grow or to remember who it is.”
