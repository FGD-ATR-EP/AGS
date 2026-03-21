# Aetherium Genesis Platform Audit + Work Plan

## 1) Code/ABI discovery summary

### 1.1 VisualParameters and Embodiment ABI
- `VisualParameters` carries render-facing fields via `visual_parameters`: `base_shape`, `turbulence`, `particle_density`, `color_palette`, and `flow_direction`.
- `EmbodimentContract` carries UI-driving inputs under `temporal_state`, `cognitive`, and `intent`:
  - Inputs: `phase`, `stability`, `duration_ms`, `effort`, `uncertainty`, `latency_factor`, `category`, `purity`.
  - Output path: `EmbodimentAdapter.translate(...) -> VisualParameters`.

### 1.2 `intent_vector` contract surface
- Bus contract `formation.schema.json` requires `intent_vector` + `motion_class`.
- Kernel publishes `intent_vector` into event extensions and reconstructs it for subscribers.

### 1.3 GunUI responsibility check
- Spec says visual output must be truthful, state-bound, and avoid decorative use:
  - Embodiment Contract: "observable truth", "No Smoothing" at contract layer, and `IDLE` should minimize to "Pilot Light".
  - Light Protocol: rejects decoration/media usage.
  - Goal Lock: "Light is Language, Not Effect", state-first sequence.
- Current GunUI implementation (`src/frontend/public/gunui/index.html`) is stateful but has legacy fallbacks that can over-render:
  - On `LOGENESIS_RESPONSE`/`LightInstruction`, it maps to hardcoded default `{cloud, #FFFFFF, turbulence=0.1}`.
  - In `applyVisualParams`, any non-manifestation mode can force `RESONATING` from `IDLE/PROCESSING`, which may reduce strict "pilot light" behavior.

## 2) Color and mood analysis

## 2.1 AM-UI color system reference status
No file explicitly named "AM-UI Color System" was found in this repository. The closest normative color/state references are:
1. `docs/EMBODIMENT_CONTRACT.md` (temporal + intent mapping),
2. `docs/LIGHT_PROTOCOL.md` (color as uncertainty/context signal),
3. `docs/ENTROPY_ECONOMY_TECHNICAL_SPEC_TH.md` (Predictable/Divergent/Chaotic mapping),
4. `src/backend/genesis_core/logenesis/embodiment.py` (actual color values used in temporal visuals).

## 2.2 Consolidated state/intent -> color mapping (observed)

| Lifecycle/Intent | Expected Color (spec/adapter) | Sources |
|---|---|---|
| IDLE | Minimal/pilot light (not explicitly hex-coded in contract) | Embodiment Contract + Goal Lock |
| LISTENING | White `#FFFFFF` | EmbodimentAdapter temporal visuals |
| THINKING | Orange/Gold `#FFA500` | EmbodimentAdapter temporal visuals |
| ANALYTIC intent | Cyan `#00FFFF` | EmbodimentAdapter intent mapping |
| CREATIVE intent | Magenta `#FF00FF` | EmbodimentAdapter intent mapping |
| SYSTEM_OPS intent | Green `#00FF00` | EmbodimentAdapter intent mapping |
| Predictable entropy packet | Gray/White | Entropy Economy spec |
| Divergent entropy packet | Orange/Purple | Entropy Economy spec |
| Chaotic/Genius entropy packet | Gold + particle explosion | Entropy Economy spec |

## 2.3 Compliance/mismatch findings
1. **Legacy fallback overrides semantics:** GunUI `legacyToVisual` always returns `cloud + #FFFFFF + turbulence 0.1`; this may erase contract-derived color semantics.
2. **Javana reflex palette drift:** `SHIELD` uses cyan `#06b6d4` (close to analytic cyan but not exact); `FLASH` uses white for high-chaos burst, while entropy spec suggests gold for chaotic/genius scenarios.
3. **Idle strictness risk:** automatic transition from `IDLE/PROCESSING` to `RESONATING` in `applyVisualParams` can conflict with "Silence is Valid / Pilot Light" intent.

## 3) Performance and latency analysis

## 3.1 Benchmark script status
A script named `latency_perception_benchmark.py` did not exist. Added `scripts/latency_perception_benchmark.py` for repeatable latency statistics:
- Input: JSON array or NDJSON records.
- Fields: supports `perceived_latency_ms` directly or computes from `latency_ms` + optional `latency_factor`.
- Output: samples, mean, p95, pass/fail against target (`<= 120ms`).

## 3.2 Available latency samples
No production telemetry dump was found in repo logs. `server_log.txt` contains startup/shutdown logs only.
For a reproducible baseline sample, we used values from reliability tests (`120`, `220`, `180`, `200` ms) to run the benchmark script.

## 3.3 Result snapshot (sample-based)
- mean: `180.0 ms`
- p95: `217.0 ms`
- target check (`<=120 ms`): **FAIL**

> Note: this is test-derived data, not live production telemetry.

## 4) Test-plan and reliability assessment

## 4.1 Existing requirements (extracted)
- Entropy test plan includes predictable/noise/creative/load cases and latency target for validator+bus (`< 50 ms`) in TC-04.
- Reliability scorecard tracks latency, correction rate, safety overrides and computes health status.
- Embodiment tests validate contract schema, topology mapping, and temporal override behavior.

## 4.2 Missing test scenarios
1. **Determinism gate for visual mapping:** same EmbodimentContract should produce stable, exact visual outputs for all enum combinations.
2. **Color policy conformance tests:** enforce state/intent->color table (including entropy feedback modes) and reject drift.
3. **Chaos/morphing regression test:** verify no uncontrolled shape jitter when repeatedly applying alternating `base_shape` with high turbulence.
4. **Idle pilot-light invariant test:** ensure IDLE never escalates to high-density/high-noise rendering without explicit state transition.
5. **Perceived-latency E2E benchmark:** websocket round-trip + first-visible-state latency distribution with p95 gate <= 120 ms.

## 5) Platform work decomposition (/CREATE_PLATFORM_WORK)

## 5.1 Workstreams
- **Architecture:** ABI boundary hardening (EmbodimentContract -> adapter -> renderer), fallback path reduction.
- **Protocol:** canonical color/state protocol (single source), intent_vector schema/versioning.
- **Reliability:** invariants for determinism, pilot-light, safety override auditability.
- **Benchmark:** perceived-latency harness, replayable traces, regression gates.
- **Ops:** telemetry pipeline + dashboards + alert thresholds.
- **Migration:** legacy GunUI path cleanup and phased rollout to protocol-compliant rendering.

## 5.2 Backlog (Epic -> Story -> Task with measurable AC)

### Epic A — Contract Fidelity
- Story A1: Normalize Embodiment -> Visual mapping.
  - Task A1.1: Create single mapping table for temporal + intent colors in code/docs.
    - AC: 100% enum coverage test; no unknown default for known enums.
  - Task A1.2: Remove hardcoded `legacyToVisual` neutral fallback for contract-capable messages.
    - AC: `LOGENESIS_RESPONSE` retains upstream color/shape in integration test.

### Epic B — Latency Quality Gate
- Story B1: Establish perceived-latency benchmark.
  - Task B1.1: Maintain script-based benchmark in CI.
    - AC: CI publishes mean/p95 and fails if p95 > 120ms.
  - Task B1.2: Add websocket capture fixture for first-visual-event timing.
    - AC: >= 500 samples/run; confidence interval exported.

### Epic C — GunUI Experience Integrity
- Story C1: Enforce anti-spam rendering semantics.
  - Task C1.1: Add IDLE pilot-light guard.
    - AC: IDLE frame entropy stays below configured threshold for 99% frames.
  - Task C1.2: Add morphing chaos regression test.
    - AC: shape-stability metric remains within tolerance (<5% outlier frames).

### Epic D — Reliability/Safety
- Story D1: Expand reliability scorecard.
  - Task D1.1: Add p95 latency and state-transition error rate.
    - AC: API returns new fields; tests assert value ranges.
  - Task D1.2: Add safety+visual conformance correlation report.
    - AC: daily report generated with non-null counts and trend lines.

## 5.3 Options + tradeoffs
1. **Option 1: Strict adapter-centric mapping (Recommended)**
   - Pros: deterministic, testable, single source of truth.
   - Cons: less stylistic flexibility in frontend experiments.
2. **Option 2: Frontend-owned adaptive mapping**
   - Pros: faster iteration on visuals.
   - Cons: high drift risk; harder protocol compliance; color inconsistency.
3. **Option 3: Hybrid with feature flags**
   - Pros: safer migration path.
   - Cons: temporary complexity and duplicated logic.

**Chosen:** Option 1 with short-lived Option 3 flags during migration.

## 5.4 Risks / failure modes / mitigation
- Risk: protocol drift between docs/backend/frontend.
  - Mitigation: generated mapping artifact + contract tests in CI.
- Risk: perceived latency regressions after stricter validation.
  - Mitigation: staged rollout + p95 gate + rollback switch.
- Risk: visual spam from fallback paths.
  - Mitigation: IDLE/pilot-light invariant + runtime guardrails.

## 5.5 Rollout / rollback
- **Phase 1 (Week 1, Owner: Backend):** canonical mapping table + adapter tests.
- **Phase 2 (Week 2, Owner: Frontend):** GunUI consumes canonical mapping; legacy path behind flag.
- **Phase 3 (Week 3, Owner: SRE/Ops):** benchmark gates + dashboards + alerts.
- **Rollback:** toggle feature flag to legacy path; keep telemetry and incident record; restore previous adapter mapping from tagged release.

## 5.6 Production Definition of Done
- Tests: unit + integration + conformance + chaos regression all green.
- SLO gates: perceived p95 <= 120ms; validator/bus target maintained.
- Benchmarking gates: no >10% regression from baseline on mean and p95.
- Observability: latency histograms, state-transition counters, override rates.
- Runbooks: incident, degraded-mode, rollback procedures documented.
- Security checks: dependency scan, secrets policy, safety override audit trail.

## 6) Redundancy elimination principle
To keep one complete source of truth, duplicated mapping logic should be removed from:
- frontend legacy defaults,
- ad-hoc reflex palettes that conflict with protocol semantics,
- parallel doc tables that do not reflect runtime behavior.

A single generated mapping artifact should drive backend adapter, frontend renderer, tests, and docs.
