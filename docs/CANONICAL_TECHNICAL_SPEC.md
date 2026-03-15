# AETHERIUM-GENESIS Canonical Technical Specification

## 1. Repository Analysis (Concise)

- The repository is implemented as a FastAPI-based AI platform with explicit backend/frontend separation under `src/backend` and `src/frontend`.
- Runtime control and orchestration are backend-first: `src/backend/main.py` initializes bus, cognition engine, governance, entropy/memory services, routers, and static serving.
- Core architecture is present in code as subsystem modules:
  - Reasoning (Logenesis + agents)
  - Governance (risk tiering, approval routing)
  - Bus (AetherBus event transport)
  - Execution adapters (vessels)
  - Memory (Akashic ledger and projections)
  - Frontend manifestation surfaces (PWA/dashboard/GunUI pages)
- Protocol surfaces are strongly schema-oriented (Pydantic models and JSON schema), though mixed generation-era docs include both canonical and legacy language.

## 2. System Purpose

AETHERIUM-GENESIS is an AI Operating System platform that converts human/system intent into governed, auditable action and manifests resulting state to operators.

Canonical operational loop:

`Intent -> Reasoning -> Policy Validation -> Execution -> Memory Commit -> Manifestation`

The platform goal is deterministic, inspectable, and replayable operation across internal cognition, governance controls, execution adapters, and human-facing manifestation.

## 3. Architectural Scope

### 3.1 In Scope

- **Mind (Reasoning):** intent interpretation and response synthesis (`logenesis`, cognitive agents).
- **Kernel (Governance):** policy/risk tiering, approvals, and enforcement gates.
- **Bus (Transport):** explicit event envelope transport across components.
- **Hands (Execution):** vessels/adapters for external actions.
- **Memory (Continuity):** append-only records and derived projections.
- **Body (Manifestation):** frontend rendering of state/directives.

### 3.2 Out of Scope

- Frontend-authored cognition or policy decisions.
- Unvalidated action execution paths bypassing governance controls.
- “UI-first” semantic behavior not grounded in backend protocols.

## 4. Subsystem Boundaries

### 4.1 Mind (Reasoning)

- **Primary modules:** `src/backend/genesis_core/logenesis/*`, `src/backend/genesis_core/agents/agio_sage.py`.
- **Responsibilities:** interpret intent, produce cognitive/manifestration outputs, maintain reasoning state.
- **Interface contract:** receives/returns typed intent/event models; does not directly mutate UI semantics.

### 4.2 Kernel (Governance)

- **Primary modules:** `src/backend/genesis_core/governance/core.py`, `src/backend/genesis_core/agents/validator.py`, `src/backend/routers/governance.py`.
- **Responsibilities:** risk tier assessment, approval request lifecycle, policy simulation, audit logging.
- **Boundary rule:** any execution-capable intent classified as execution request must pass governance audit/approval gates.

### 4.3 Bus (AetherBus)

- **Primary modules:** `src/backend/genesis_core/bus/extreme.py`, `src/backend/genesis_core/protocol/schemas.py`, `src/backend/genesis_core/bus/contracts/formation.schema.json`.
- **Responsibilities:** event publishing/subscription, targeted/broadcast dispatch, global listeners for observability.
- **Boundary rule:** cross-subsystem communication uses explicit event envelopes and typed schemas.

### 4.4 Hands (Execution/Vessels)

- **Primary modules:** `src/backend/vessels/*`, `src/backend/genesis_core/vessels/*`.
- **Responsibilities:** action adapters into external systems (workspace, drive, slack, database).
- **Boundary rule:** no vessel call path should bypass governance for high-impact actions.

### 4.5 Memory (Akashic)

- **Primary modules:** `src/backend/genesis_core/memory/akashic.py`, entropy ledger modules.
- **Responsibilities:** append-only chain records with provenance/hash continuity; derived projections (episodic/semantic/gems).
- **Boundary rule:** memory is an architectural artifact, not optional debug logging.

### 4.6 Body (Frontend Manifestation)

- **Primary modules:** `src/frontend/index.html`, `src/frontend/dashboard.html`, `src/frontend/public/dashboard/*.js`, `src/frontend/public/gunui/*`.
- **Responsibilities:** render backend state, approvals, and visual manifestation.
- **Boundary rule:** frontend is manifestation-only; it must not invent intent/governance semantics.

## 5. Canonical Data and Control Flow

1. **Intent Ingestion**
   - Session handshake (`POST /v1/session`) validates identity/key context.
   - Stream channel (`/ws/v3/stream`) accepts user text/intent payloads.
2. **Reasoning Trigger**
   - Intent packets are transformed into `SystemIntent` and sent to reasoning path.
3. **Policy Validation**
   - Validator applies signature/rules and governance risk/approval checks.
4. **Execution Decision**
   - Low-tier operations auto-allow by policy; higher tiers generate pending approvals.
5. **Execution (when allowed)**
   - Approved intents are eligible for execution through vessels/adapters.
6. **Memory Commit**
   - Governance decisions and system events are appended to Akashic ledger with provenance and hash linkage.
7. **Manifestation**
   - Typed bus events (`AetherEvent`) are emitted to frontend channels for rendering and operator controls.

## 6. Protocol and Message Roles

### 6.1 Core Intent Envelope

- `SystemIntent` is the inter-agent intent packet with immutable identity (`vector_id`), origin/target, context, payload, and optional correlation/signature.
- `IntentPayload` encapsulates modality-specific content and encryption metadata.

### 6.2 Bus Envelope

- `AetherEvent` is the canonical transport envelope for state, intent, manifestation, and error signals.
- `AetherEventType` defines lifecycle/control events (`intent_detected`, `manifestation`, `degradation`, `handshake`, etc.).

### 6.3 Entropy and Memory Protocol

- Entropy subsystem uses typed packet/assessment schemas (`EntropyPacket`, `EntropyAssessment`, submit/replay/explorer responses).
- Ledger continuity is represented by explicit hash chain fields and continuity reports.

### 6.4 ABI/Embodiment Contract

- Manifestation mapping is contract-driven (`EmbodimentContract`/`VisualParameters`) and should remain stable for frontend consumers.
- Contract semantics must dominate fallback UI heuristics.

## 7. Governance Boundaries

- Governance implements action tiering (`Tier 0` read-only through `Tier 3` sensitive/irreversible).
- Execution-risk intents requiring review must create `ApprovalRequest` records and remain blocked until explicit decision.
- Governance outcomes and simulations must be auditable via memory records.
- No runtime path may elevate autonomy beyond policy without explicit approval and audit recordability.

## 8. Execution Model

- Runtime host is FastAPI with routers for session/stream, governance, metrics, and entropy.
- Startup lifecycle initializes:
  - reasoning lifecycle engine
  - AetherBus connection
  - security key manager
  - entropy validator/replay/treasury
  - metrics loop and health broadcast
- Execution path must preserve ordering:
  - validated input -> governed decision -> action pathway -> memory commit -> outward manifestation.

## 9. Memory Model

### 9.1 Canonical Store

- `data/akashic_records.json` serves as append-only chain with:
  - payload
  - provenance (`actor`, `intent_id`, `causal_link`)
  - hash linkage (`prev_hash`, `hash`)

### 9.2 Integrity Requirements

- Chain integrity must be verifiable (hash recomputation and linkage validation).
- Temporal consistency must be monotonic.
- Derived projections (`episodic`, `semantic`, `gems`) are rebuildable views, not source-of-truth replacements.

### 9.3 Entropy Ledger

- Entropy treasury ledger maintains additional continuity surface (`hash_prev`, `hash_self`, chain head, continuity checks).

## 10. Frontend Manifestation Constraints

- Frontend must consume backend protocols/directives and render state truthfully.
- Frontend must not:
  - infer or author intent semantics independently,
  - perform policy decisions,
  - convert decorative state into authoritative behavior.
- Idle/low-activity states should remain minimal and state-bound (pilot-light principle).
- Visual protocol changes require schema/contract updates before UI behavior changes.

## 11. Source-of-Truth Hierarchy

When definitions conflict, apply this precedence:

1. Governance and safety constraints.
2. Canonical protocol/schema definitions (typed models and contracts).
3. Memory continuity/auditability requirements.
4. Core subsystem boundaries (mind/kernel/bus/hands/memory/body).
5. Runtime implementation details.
6. Visual/experiential preferences.

## 12. Invariants and Non-Goals

### 12.1 Invariants

- Governance must gate execution.
- Memory commit is part of product behavior, not optional telemetry.
- Subsystems communicate through explicit schemas/envelopes.
- Frontend is manifestation, not cognition.
- Protocol stability is higher priority than visual novelty.

### 12.2 Non-Goals

- UI-only novelty lacking architectural value.
- Additional autonomous behavior without governance/audit controls.
- Hidden cross-subsystem coupling or untyped ad hoc message paths.

## 13. Integration Expectations

- Integrations should connect through bus/events or typed API surfaces, not direct internal coupling.
- External adapters (vessels) must expose action metadata suitable for risk assessment and approval preview.
- New protocol surfaces require:
  - explicit schemas,
  - backward-compatibility strategy (or documented migration/deprecation),
  - audit and memory implications documented.

## 14. Validation Expectations

- **Schema validation:** input/output payloads use typed Pydantic models and/or JSON schema.
- **Governance validation:** execution-capable intents are tested for tiering and approval routing.
- **Memory validation:** hash-chain and temporal consistency checks are mandatory for ledger integrity paths.
- **Flow validation:** critical loop is testable end-to-end (`Intent -> Reasoning -> Policy Validation -> Execution -> Memory Commit -> Manifestation`).
- **Frontend validation:** UI behavior must be checked against protocol contract conformance, not only visual output.

## 15. Conflicts and Drift Notes (Docs vs Implementation)

1. **Legacy/Theatrical documentation drift:** some documents describe obsolete prototype/disconnected architecture, while current repository runs an integrated FastAPI + router + bus runtime.
2. **Mixed canonical language:** several docs contain manifesto/vision framing that is not directly executable specification; runtime behavior is defined more reliably by code-level schemas and routers.
3. **Frontend conformance risk acknowledged by audits:** platform audit docs identify legacy GunUI fallback behavior that may dilute strict state-to-visual fidelity; this should be treated as known technical debt.
