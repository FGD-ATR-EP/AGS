# Unified AI-OS Integration Guide

This document defines the cross-repository integration contract for the Phase 1 unified AI-OS deployment spanning:

- `AETHERIUM-GENESIS`
- `PRGX-AG`
- `AetherBus-Tachyon`

## Canonical repository roles

| Repository | Canonical role | Runtime responsibility |
| --- | --- | --- |
| `AETHERIUM-GENESIS` | Mind + Body orchestration surface | Intent ingress, directive preparation, manifestation delivery, local service composition |
| `PRGX-AG` | Governance kernel source | Policy evaluation, approval routing, execution gating, risk inspection |
| `AetherBus-Tachyon` | Canonical event bus | Internal ZeroMQ transport, external WebSocket bridge, envelope propagation |

## Cross-repo setup

### 1. Shared protocol contract

All repositories must exchange the same V3 envelope structure:

- `envelope_version=3.0.0`
- `protocol_version=2026.03`
- `correlation_id` created at origin
- `causation_id` preserved across derived events
- `trace_id` preserved across replay and manifestation surfaces
- `origin`, `target`, `topic`, `payload`, `governance`, `memory`, `timestamps`, `content`

See also:
- `docs/directive_envelope_standard.md`
- `docs/AETHERBUS_TACHYON_INTEGRATION.md`

### 2. Runtime endpoint contract

| Variable | Default | Used by |
| --- | --- | --- |
| `BUS_IMPLEMENTATION` | `tachyon` | AETHERIUM-GENESIS |
| `BUS_INTERNAL_ENDPOINT` | `tcp://127.0.0.1:5555` | AETHERIUM-GENESIS + AetherBus-Tachyon |
| `BUS_EXTERNAL_ENDPOINT` | `ws://127.0.0.1:5556/ws` | AETHERIUM-GENESIS + external UI consumers |
| `AETHERBUS_TACHYON_INTERNAL_ENDPOINT` | alias | Cross-repo deployment templates |
| `AETHERBUS_TACHYON_EXTERNAL_ENDPOINT` | alias | Cross-repo deployment templates |

### 3. Recommended startup order

1. Start `AetherBus-Tachyon` internal/external bridge endpoints.
2. Start `PRGX-AG` governance services with access to the same envelope schema and correlation policy.
3. Start `AETHERIUM-GENESIS` with `BUS_IMPLEMENTATION=tachyon`.
4. Attach UI/operator clients only through the external WebSocket bridge.

## Governance requirements

No execution-capable path may bypass governance.

### Mandatory gates

1. **Intent ingress** must normalize raw input into a V3 envelope.
2. **Governance kernel** must evaluate risk and emit an inspectable decision.
3. **Approval-required actions** must stop until approval state is recorded.
4. **Execution adapters** may run only on governance-validated directives.
5. **Execution outcomes** must emit follow-up envelopes and memory records.

### Required governance metadata

Every governed handoff must preserve:

- `governance.policy_mode`
- `governance.validated`
- `governance.decision` when policy has executed
- `governance.risk_tier` for inspectable controls
- `governance.approval_ticket_id` when human approval is required

## Memory continuity guarantees

Akashic-style continuity is a product requirement, not a debug convenience.

### Required guarantees

- **Append-only canonical records** for governed lifecycle events.
- **Correlation-linked replay** using `correlation_id`, `causation_id`, and `trace_id`.
- **Deterministic provenance** between intent, governance decision, execution outcome, and manifestation.
- **Queryable export path** for audits, replay tooling, and compliance reporting.
- **Derived projections** must never become the source of truth over the canonical ledger/event stream.

### Minimum governed cycle

`Intent ingress -> V3 envelope -> Governance decision -> Approval outcome (if required) -> Execution outcome -> Memory commit -> Manifestation`

Every phase above must keep the same correlation chain.

## Migration notes

- Legacy in-process bus paths remain compatibility-only; they are not the canonical deployment target.
- `session_id` may still backfill correlation metadata for older producers, but new producers must emit canonical fields directly.
- Frontend clients must remain render-only consumers of backend directives and must not synthesize semantic state locally.

## Phase 1 boundary

This document intentionally stays focused on Phase 1:

- canonical Tachyon bus adoption
- governance-first envelope handoff
- memory continuity requirements
- migration-safe runtime configuration

Later phases should land in separate PRs for projection workers, replay tooling, approval bridges, and broader cross-repo contract harnesses.
