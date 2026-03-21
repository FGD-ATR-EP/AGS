# Directive Envelope Standard (V3)

This document defines the canonical directive envelope used to connect Intent, Reasoning, Governance, Execution, Memory commit, and Manifestation.

## Objectives

- Provide one stable packet shape for cross-subsystem traceability.
- Preserve replayability in Akashic Memory.
- Preserve governance-first execution gates with explicit risk and approval metadata.

## Canonical schema

```json
{
  "envelope_version": "3.0.0",
  "protocol_version": "2026.03",
  "envelope_id": "uuid",
  "type": "intent_detected|manifestation|degradation|...",
  "correlation_id": "uuid-created-at-origin",
  "causation_id": "uuid-or-null",
  "origin": {
    "service": "api|genesis_core|governance|memory|tachyon",
    "subsystem": "body|mind|kernel|memory|bus",
    "instance": "optional-runtime-instance",
    "channel": "session-or-stream-id"
  },
  "target": {
    "service": "client|genesis_core|governance|memory|broadcast",
    "subsystem": "manifestation|mind|kernel|memory|bus",
    "instance": "optional-runtime-instance",
    "channel": "session-or-stream-id"
  },
  "topic": "intent.ingress",
  "payload": {},
  "governance": {
    "decision": "ALLOWED|DENIED|PENDING_APPROVAL|null",
    "risk_tier": "TIER_0..TIER_3|null",
    "policy_effect": "ALLOW|DENY|REQUIRE_APPROVAL|null",
    "policy_mode": "enforce|dry_run",
    "approval_ticket_id": "string|null",
    "validated": true
  },
  "memory": {
    "ledger_event_type": "intent_ingress|governance_allowed|execution_completed|...",
    "ledger_record_id": "string|null",
    "causal_chain": ["uuid"],
    "replayable": true
  },
  "timestamps": {
    "created_at": "2026-03-18T00:00:00+00:00",
    "published_at": "2026-03-18T00:00:00+00:00",
    "consumed_at": "2026-03-18T00:00:00+00:00"
  },
  "content": {
    "content_type": "application/json",
    "content_encoding": "identity",
    "content_compression": "none",
    "codec": "json|msgpack"
  },
  "extensions": {
    "bus_metadata": {
      "codec": "json|msgpack",
      "compression": "none|zlib",
      "content_encoding": "identity"
    }
  }
}
```

## Compatibility rules

1. New fields must be additive and optional within a minor version.
2. Removing or renaming fields requires a major version bump.
3. Producers and consumers must validate `envelope_version`, `protocol_version`, `topic`, and `correlation_id` before processing.
4. Governance metadata (`policy_mode`, `validated`) is mandatory for every governed runtime handoff. Executable directives additionally require `decision` / `risk_tier` once policy has run.

## Runtime requirements

- All execution-capable flows must log envelope-correlated governance events.
- Dry-run decisions must be tagged with `policy_mode=dry_run` and must not produce irreversible side effects.
- Envelope IDs, correlation IDs, and causation IDs must be persisted into Akashic records for replay and audit exports.

## Validation boundaries in runtime

- **API ingress:** raw client payloads are upgraded into V3 envelopes before entering directive runtime handling.
- **Directive runtime:** all human intent and system-triggered executable directives must pass `Intent normalization -> Governance evaluation -> Approval routing -> Execution readiness` before planner or vessel dispatch.
- **Bus publish / consume:** `BaseAetherBus` validates V3 requirements before serialization and after decode.
- **Governance gate:** `GovernanceCore.validate_envelope(...)` and `evaluate_envelope(...)` validate the full envelope context before policy/risk evaluation.
- **Vessel execution path:** execution adapters must validate the envelope before simulating or executing side effects.
- **Vessel execution path:** executable directive payloads must include `action`, `params`, `execution_scope`, `actor`, and `metadata`; adapters must reject hardcoded credentials and log an Akashic `execution_outcome` before returning.

## Correlation policy

The protocol layer defines one canonical correlation policy for replayable envelopes:

- `correlation_id` must exist on every envelope and represent the governed execution cycle.
- `causation_id` should point to the parent envelope, approval request, or execution precursor when applicable.
- `trace_id` must remain stable across bus transport, governance records, websocket manifestation payloads, and memory projections.
- If a client omits these values at ingress, the backend must create them before the first publish.
- UI payloads should surface this metadata via backend-authored `directive_state`; frontend code must not infer or rewrite correlation semantics locally.

### Replay checklist

1. Find the origin envelope by `correlation_id`.
2. Walk `causation_id` links to reconstruct the event chain.
3. Use `trace_id` to join UI, governance, and memory views for the same execution cycle.
4. Confirm ledger/projection records preserve the same metadata before replaying side effects.


## Canonical manifestation directive contract

Frontend manifestation consumers may only render backend-authored directive payloads. They must not generate semantic meaning, intent classification, governance status, or execution state locally.

### Allowed frontend fields

```json
{
  "manifest_version": "2026.03-manifestation-v1",
  "frontend_contract": "render-only",
  "semantic_source": "backend",
  "directive_state": {
    "correlation_id": "corr-...",
    "causation_id": "env-...",
    "trace_id": "trace-...",
    "topic": "manifestation.response",
    "directive_type": "manifestation",
    "manifest_version": "2026.03-manifestation-v1",
    "session_id": "ae-1234",
    "lifecycle_stage": "manifestation_emit",
    "sandbox": false
  },
  "render_state": {},
  "status": {},
  "replay": {},
  "diagnostics": {}
}
```

### Frontend restrictions

The client may:
- render `render_state`
- display `status`
- expose replay controls using `replay`
- expose inspectable metadata using `diagnostics` and `directive_state`

The client must not:
- infer intent, risk tier, or execution meaning from visuals
- synthesize new semantic states from particle behavior, color, motion, audio level, or timing
- rewrite `correlation_id`, `trace_id`, `topic`, or `manifest_version`
- upgrade sandbox/demo output into canonical runtime state

Sandbox/demo pages must be explicitly labeled `sandbox=true` and treated as non-canonical surfaces.

## Migration notes from legacy envelopes

Legacy `AetherEvent` packets and `AkashicEnvelope` instances are automatically upgraded when possible:

- legacy `session_id` becomes the default `topic` and fallback `correlation_id`
- legacy `state`, `intent`, `manifestation`, and `error` blocks are copied into canonical `payload`
- legacy `extensions.bus_metadata.codec/compression` populate `content.codec` and `content.content_compression`
- `AkashicEnvelope` now wraps `AetherEvent` and should be treated as a compatibility shim only

## End-to-end example

```json
[
  {
    "type": "intent_detected",
    "topic": "intent.ingress",
    "correlation_id": "corr-7f4f",
    "causation_id": null,
    "origin": {"service": "api", "subsystem": "body", "channel": "ae-1234"},
    "target": {"service": "genesis_core", "subsystem": "mind", "channel": "lifecycle"},
    "payload": {"text": "summarize the audit log"},
    "governance": {"policy_mode": "enforce", "validated": true},
    "memory": {"ledger_event_type": "intent_ingress", "causal_chain": ["corr-7f4f"], "replayable": true}
  },
  {
    "type": "state_update",
    "topic": "governance.decision",
    "correlation_id": "corr-7f4f",
    "causation_id": "corr-7f4f",
    "origin": {"service": "governance", "subsystem": "kernel"},
    "target": {"service": "genesis_core", "subsystem": "hands"},
    "payload": {"action": "read_file", "resource": "audit.log"},
    "governance": {"decision": "ALLOWED", "risk_tier": "TIER_0_READ_ONLY", "policy_effect": "ALLOW", "policy_mode": "enforce", "validated": true},
    "memory": {"ledger_event_type": "governance_allowed", "causal_chain": ["corr-7f4f"], "replayable": true}
  },
  {
    "type": "manifestation",
    "topic": "manifestation.response",
    "correlation_id": "corr-7f4f",
    "causation_id": "corr-7f4f",
    "origin": {"service": "genesis_core", "subsystem": "mind"},
    "target": {"service": "client", "subsystem": "manifestation", "channel": "ae-1234"},
    "payload": {"system_intent": {"intent_type": "COGNITIVE_RESPONSE"}},
    "governance": {"policy_mode": "enforce", "validated": true},
    "memory": {"ledger_event_type": "manifestation_emit", "causal_chain": ["corr-7f4f"], "replayable": true}
  }
]
```
