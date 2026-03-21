# AETHERIUM GENESIS (AG-OS)
### Unified AI-OS Platform Overview

![Version](https://img.shields.io/badge/version-2.2.0--resonance-blueviolet.svg)
![Status](https://img.shields.io/badge/status-ACTIVE-success.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Current state

AETHERIUM-GENESIS is being aligned as a unified AI operating system with clear subsystem boundaries:

- **Mind**: intent interpretation and directive preparation.
- **Kernel**: governance and approval through PRGX-AG-aligned policy enforcement.
- **Bus**: AetherBus-Tachyon as the canonical event transport.
- **Hands**: vessels/adapters that execute only governance-approved directives.
- **Memory**: Akashic-style immutable continuity records.
- **Body**: UI/PWA manifestation surfaces that render backend directives only.

## Architecture summary

### Canonical control loop

`Intent -> Reasoning -> Policy Validation -> Execution -> Memory Commit -> Manifestation`

### Unified AI-OS roles

| Layer | Component | Responsibility |
| --- | --- | --- |
| System bus | AetherBus-Tachyon | ZeroMQ internal transport, WebSocket bridge, envelope propagation |
| Governance kernel source | PRGX-AG | Policy evaluation, approval gates, risk-aware control |
| Memory fabric | Akashic | Immutable records, replay continuity, audit joins |
| Manifestation plane | UI / PWA | Render-only client for backend-authored directives |

## Phase 1 focus

- Tachyon is the preferred runtime bus.
- V3 `AetherEvent` envelopes are the canonical cross-subsystem contract.
- Correlation metadata must be preserved end-to-end.
- Legacy bus implementations remain compatibility-only.

## Dependency installation

```bash
pip install -r requirements.txt
```

Optional ML / visual stack:

```bash
pip install -r requirements/optional-ml-visual.txt
```

Development and test stack:

```bash
pip install -r requirements/dev.txt
```

See [`docs/dependency_inventory.md`](dependency_inventory.md) for the full dependency classification.

## Migration phases

1. **Phase 1** — canonical Tachyon bus path and V3 envelope enforcement.
2. **Phase 2** — PRGX-AG approval outcome bridge and stronger governance kernel integration.
3. **Phase 3** — Akashic replay tooling and derived projection workers.
4. **Phase 4** — cross-repo deployment profiles, rollback drills, and contract harnesses.

## Proposed next functions / extensions

- **Cross-Repo Contract Harness**: verify protocol, approval, and memory continuity across the three repositories.
- **Governed Replay Console**: inspect one `correlation_id` lifecycle across bus, governance, execution, and memory.
- **Deployment Profiles**: define shared local/staging/production runtime profiles.
- **Directive Catalog**: formalize stable backend-authored manifestation directives.
- **Projection Workers**: derive operator/search views from the canonical stream without mutating source-of-truth records.
- **Approval Outcome Bridge**: emit PRGX-AG approval outcomes as standard V3 envelopes.

## References

- [`../README.md`](../README.md)
- [`AETHERBUS_TACHYON_INTEGRATION.md`](AETHERBUS_TACHYON_INTEGRATION.md)
- [`UNIFIED_AI_OS_INTEGRATION.md`](UNIFIED_AI_OS_INTEGRATION.md)
- [`directive_envelope_standard.md`](directive_envelope_standard.md)
