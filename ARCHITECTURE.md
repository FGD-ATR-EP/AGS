# Architecture & Canon

## Two-Layer Language Model (Vision + Engineering)

### 1) Vision Language
- Resonance / Resonators
- Inspira-Firma duality
- AetherBus Tachyon / Negative Latency
- AG-OS mythos and philosophical framing

### 2) Engineering Language
- **Cognitive Core**: reasoning, planning, validation
- **Execution Vessel Layer**: operational actions in scoped environments
- **Governance Core**: policy-as-code, action tiering, human approval routing
- **Memory Fabric**: canonical Akashic stream + episodic/semantic/procedural/reflective/identity projections
- **Reflector + Gem Lifecycle**: incident-to-learning discipline
- **Approval Workflow**: preview → approval inbox → execution → immutable provenance

## Canonical Data Flow

`Intent -> Plan -> Governance Evaluation -> Approval (if needed) -> Vessel Execute -> Outcome -> Reflection -> Gem -> Memory Projection`

## Canonical Event Source

- `data/akashic_records.json` is the immutable, append-only source of truth.
- Projections under `data/memory/**` are derived, rebuildable views.

## External Embodied Knowledge

AETHERIUM GENESIS does not encode formation knowledge internally.

All semantics related to:
- Intent → Motion
- Light emergence
- Voice-reactive embodiment

are canonically defined in:

**The Book of Formation – AETHERIUM GENESIS**
https://github.com/lnspirafirmaGPK/The-Book-of-Formation-AETHERIUM-GENESIS

This repository operates in conformance with that body of knowledge.


## Manifestation Surface Boundary

Frontend surfaces are manifestation clients, not logic engines. The canonical UI contract is the backend-authored manifestation directive carried inside the V3 envelope and exposed over the `/ws/v3/stream` bridge.

- Backend responsibilities: author `directive_state`, `render_state`, `status`, `replay`, and `diagnostics`; preserve `correlation_id` / `trace_id`; set `manifest_version`.
- Frontend responsibilities: render those fields, display status, expose replay controls, and surface diagnostics.
- Forbidden on the client: semantic inference, governance reinterpretation, execution-state invention, or correlation rewriting.
- Demo/sandbox pages under `src/frontend/public/gunui/` remain non-canonical unless explicitly wired to the directive bridge and labeled otherwise.
