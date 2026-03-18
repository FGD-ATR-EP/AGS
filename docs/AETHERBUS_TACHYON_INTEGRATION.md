# AetherBus-Tachyon Integration Guide

## Purpose

This document defines the canonical Phase 1 bus path for AETHERIUM-GENESIS. The platform now treats **AetherBus-Tachyon** as the preferred runtime transport and keeps legacy in-process bus implementations only as compatibility layers.

Canonical path:

`Intent -> V3 Envelope -> Governance-aware Bus Publish -> Tachyon Internal ZeroMQ -> Tachyon WebSocket Bridge -> Manifestation`

## Runtime topology

### Internal microservices

- Transport: **ZeroMQ PUB/SUB**
- Default endpoint: `tcp://127.0.0.1:5555`
- Use case: internal backend components, lifecycle orchestration, governance telemetry, memory events

### External / UI consumers

- Transport: **WebSocket bridge**
- Default endpoint: `ws://127.0.0.1:5556/ws`
- Use case: dashboards, manifestation surfaces, operator consoles, replay tooling

## Configuration contract

The runtime bus implementation is selected by environment variables.

| Variable | Default | Description |
| --- | --- | --- |
| `BUS_IMPLEMENTATION` | `tachyon` | Runtime selector. Supported values: `tachyon`, `extreme`, `legacy`. |
| `BUS_INTERNAL_ENDPOINT` | `tcp://127.0.0.1:5555` | Internal ZeroMQ endpoint. |
| `AETHERBUS_TACHYON_INTERNAL_ENDPOINT` | _(alias)_ | Alias accepted for cross-repository deployment templates. |
| `BUS_EXTERNAL_ENDPOINT` | `ws://127.0.0.1:5556/ws` | External WebSocket bridge endpoint. |
| `AETHERBUS_TACHYON_EXTERNAL_ENDPOINT` | _(alias)_ | Alias accepted for cross-repository deployment templates. |
| `BUS_CODEC` | `msgpack` | Envelope payload codec (`msgpack` or `json`). |
| `BUS_COMPRESSION` | `none` | Compression metadata for transport coordination. |
| `BUS_TIMEOUT_MS` | `2000` | Publish/receive timeout budget. |
| `BUS_RECONNECT_INITIAL_DELAY_MS` | `250` | First reconnect delay. |
| `BUS_RECONNECT_MAX_DELAY_MS` | `5000` | Maximum reconnect backoff. |
| `BUS_RECONNECT_MAX_ATTEMPTS` | `10` | Maximum reconnect attempts before escalation. |

## Envelope requirements

Every cross-subsystem payload must travel inside `AetherEvent` V3 with:

- `envelope_version=3.0.0`
- `protocol_version`
- `correlation_id` created at origin and preserved end-to-end
- `origin`, `target`, and stable `topic`
- `payload`
- `governance`, `memory`, `timestamps`, and `content` metadata
- `extensions.bus_metadata.codec/compression` synchronized with canonical `content.*` metadata

This contract keeps deterministic replay and distributed tracing available to Governance Core, Akashic Memory, and manifestation surfaces.

## Compatibility layer policy

- `src/backend/genesis_core/bus/extreme.py` is retained only for local compatibility and tests.
- `src/backend/genesis_core/bus/kernel.py` is retained only as a compatibility wrapper for older intent-routing call sites.
- New runtime work must target `BusFactory -> AetherBusTachyon`.

## Integration notes for adjacent repositories

### PRGX-AG

Governance decisions should publish approval, block, escalation, and override outcomes through the canonical bus path so that policy enforcement remains inspectable.

### Aetherium-Manifest

The UI should subscribe through the WebSocket bridge and render only backend-authored directives. Frontend state must not become an alternate semantic source.

## Correlation and replay contract

Phase 1 requires a single correlation policy for every V3 envelope crossing subsystem boundaries. Implementations in AETHERIUM-GENESIS must create or normalize the following fields at the event origin:

- `correlation_id`: stable execution-cycle identifier
- `causation_id`: parent envelope or approval/execution precursor
- `trace_id`: replay/distributed-trace identifier shared across bus, governance, memory, and manifestation

### Required propagation path

1. **API ingress / intent origin** creates IDs if the client omits them.
2. **Bus publish/subscribe** preserves all three fields and mirrors them into websocket-facing directive payloads.
3. **Governance evaluation / approval routing** persists the same IDs into ledger/audit records.
4. **Memory commit** stores the IDs in canonical records and derived projections for deterministic replay.
5. **Manifestation/UI** renders backend-authored `directive_state` using the same `correlation_id` / `trace_id` chain.

### Migration notes

- Legacy `session_id` remains a compatibility fallback for `correlation_id` and `trace_id`, but new producers should send canonical fields directly.
- Compatibility bus implementations may remain available for tests, but Phase 1 runtime default remains `tachyon`.
- Replay tooling should query memory records by `correlation_id` first and use `trace_id` for cross-surface aggregation.


## Governance runtime gate

The Tachyon adapter is the canonical transport, but transport alone is not sufficient. Runtime ingress now flows through a central directive runtime that upgrades ingress payloads into `AetherEvent` envelopes, evaluates governance using full envelope context, routes approval when required, emits `governance.decision` / `execution.readiness` events, and only then authorizes lifecycle or vessel processing.


## Phase 1 migration notes

- `tachyon` remains the canonical runtime default; `extreme` and `legacy` are compatibility-only modes and now log an explicit migration warning at bus selection time.
- Subscribers may bind by bus topic or session channel, allowing governance/runtime/UI consumers to preserve the same envelope across internal transport and manifestation fan-out.
- The Tachyon adapter keeps `correlation_id`, `causation_id`, and `trace_id` intact during publish, local dispatch, and websocket fan-out.
