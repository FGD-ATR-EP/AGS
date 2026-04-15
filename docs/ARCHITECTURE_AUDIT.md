# AETHERIUM-GENESIS Architecture Audit (Canonical Alignment)

**Date:** 2026-03-15  
**Scope:** Repository audit against `AGENTS.md` and canonical design specifications.

## Design Documents Followed

1. `AGENTS.md` (canonical operating rules and subsystem laws).
2. `README.md` (current runtime architecture and subsystem map).
3. `ARCHITECTURE.md` (canonical data flow and memory source-of-truth).
4. `docs/CANONICAL_TECHNICAL_SPEC.md` (explicit architecture boundaries, invariants, and drift notes).
5. `docs/EXECUTION_MODEL.md` (execution lifecycle, atomicity, and failure-mode expectations).

## Constraints and Invariants Enforced During Audit

- Preserve canonical loop: **Intent -> Reasoning -> Policy Validation -> Execution -> Memory Commit -> Manifestation**.
- Treat frontend as **manifestation only** (no client-side cognition/policy authorship).
- Verify governance can gate execution-capable paths.
- Verify Akashic memory remains structural (append-only continuity + provenance), not debug-only.
- Prefer explicit schemas/envelopes as subsystem boundaries.
- Identify legacy surfaces that weaken canonical protocol boundaries.

## 1) Aligned Areas

### 1.1 Platform-first backend composition is present
- `src/backend/main.py` composes routers, governance, entropy, bus, metrics, and startup lifecycle into one runtime host, consistent with AI-OS control-plane direction.
- `src/backend/genesis_core/logenesis/engine.py` delegates distributed lifecycle orchestration through `LifecycleManager`, preserving backend-owned reasoning pathways.

### 1.2 Protocol/schema-first surfaces exist and are actively used
- `AetherEvent`/`AetherEventType` provide a typed transport envelope for bus propagation.
- Intent contracts (`SystemIntent`, `IntentPayload`, `IntentContext`) are used in runtime request paths.
- Governance API models (`ApprovalRequest`, decision payload models) and entropy schemas reinforce explicit contracts.

### 1.3 Governance + memory coupling is implemented at the kernel boundary
- `ValidatorAgent` invokes `GovernanceCore` for `EXECUTION_REQUEST` tiering/approval routing.
- `GovernanceCore` records approval and policy simulation outcomes to Akashic ledger via provenance-bearing events.

### 1.4 Akashic memory has first-class continuity mechanisms
- `AkashicRecords` persists append-only chain blocks with `prev_hash`/`hash` linkage and provenance metadata.
- Integrity utilities (`verify_hash_chain`, temporal consistency checks) exist and are callable.
- Projection manager derives episodic/semantic/gem views from canonical ledger.

### 1.5 AetherBus exists as shared transport boundary
- `AetherBusExtreme` centralizes publish/subscribe and global listener patterns.
- `LifecycleManager` subscribes and routes intent-linked events through bus semantics, aligning with orchestration boundary goals.

## 2) Misaligned Areas

### 2.1 Governance gate is bypassed in a canonical stream path
- In `src/backend/routers/aetherium.py`, `/ws/v3/stream` sends user intent directly to `engine.lifecycle.agio_sage.process_query(...)` instead of traversing validator/governance gate.
- This diverges from canonical sequencing where policy validation must precede execution-capable progression.

### 2.2 Legacy `/ws` and `/ws/v2/stream` paths dilute protocol stability
- `src/backend/main.py` maintains deprecated sockets with ad-hoc message types (`INTENT_RECOGNIZED`, `VISUAL_PARAMS`, `AI_SPEAK`) parallel to typed v3 event envelope usage.
- Parallel protocol surfaces increase drift risk and weaken AetherBus as the sole orchestration boundary.

### 2.3 Frontend still contains semantic/client-authored behavior in legacy interfaces
- `src/frontend/index.html` performs local voice capture, local message-type branching, and direct intent packet authorship over legacy websocket messages.
- `src/frontend/public/gunui/edge_gunui_connector.html` generates behavior from local/edge heuristic mood mapping (`system_mood`) independent of backend directive contracts.
- These patterns violate manifestation-only direction and allow client-side semantic interpretation.

### 2.4 Execution vessel layer is structurally present but not strongly governance-bound end-to-end
- Vessels define `preview/execute` contracts, but repository-wide runtime integration from governed approval -> vessel execution -> memory commit is not yet consistently wired as a single mandatory path.
- This creates potential for future direct execution coupling if new call paths are added without governance wrappers.

### 2.5 Approval lifecycle handling has a control-flow inconsistency
- `GovernanceCore.handle_approval` returns `False` on rejection after state mutation, while router currently interprets `False` as not-found and raises 404.
- This can mask real governance decisions and degrade audit/operator trust semantics.

## 3) Architectural Risks

1. **Policy bypass risk in production stream path**: direct AgioSage invocation in v3 stream can normalize cognition/action responses without kernel checkpointing.
2. **Protocol fragmentation risk**: maintaining multiple websocket dialects increases integration complexity and weakens deterministic envelope governance.
3. **Frontend semantic drift risk**: legacy UI logic may become an implicit source of intent semantics if backend contracts are not made mandatory.
4. **Execution governance gap risk**: vessel infrastructure may be consumed ad hoc without unified approval and ledger commitment pipeline.
5. **Operator/audit ambiguity risk**: rejection-not-found conflation in approval decision route can reduce inspectability and incident replay quality.

## 4) Highest-Priority Corrections

1. **Enforce validator/governance in `/ws/v3/stream` processing path** so all intent handling traverses canonical gate before downstream actions.
2. **Define one canonical websocket protocol surface** (v3 envelope-first) and place legacy sockets behind explicit deprecation toggles or adapters.
3. **Constrain frontend to rendering/backend directive consumption** by removing client-authored semantic branching from primary UI entrypoints.
4. **Codify governed execution pipeline** (`approval status -> vessel action eligibility -> mandatory memory commit`) as reusable backend orchestration utility.
5. **Fix approval decision response semantics** so rejected decisions remain successful governance outcomes (not 404 errors). ✅ Implemented in API route + governance core.

## 5) Recommended Minimal Refactors

1. In `src/backend/routers/aetherium.py`, replace direct `agio_sage.process_query` invocation with lifecycle/validator-mediated intent processing that preserves governance checkpointing.
2. In `src/backend/main.py`, retain deprecated sockets only as thin adapters translating legacy payloads into canonical `AetherEvent` envelopes; avoid duplicated logic paths.
3. In `src/frontend/index.html`, reduce network semantic logic to rendering handlers for backend-owned directives/events (no client inference of policy/intent categories).
4. In `src/frontend/public/gunui/edge_gunui_connector.html`, gate animation modes by backend-provided typed state packets instead of local heuristic mood synthesis.
5. In `src/backend/genesis_core/governance/core.py` + `src/backend/routers/governance.py`, separate `not_found` from `decision_rejected` outcomes with explicit status payloads. (Implemented.)

## Assumptions (Necessary)

- Legacy endpoints are intentionally retained for compatibility, but are treated as technical debt per canonical docs.
- Not every reasoning response currently triggers external side effects; nevertheless, governance-first invariant is evaluated on path structure, not only observed side effects.
- This audit is static/repository-based and does not claim runtime behavioral proof beyond code-path analysis.
