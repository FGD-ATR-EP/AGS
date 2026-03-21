# EXECUTION MODEL

## 1. Execution Scope
เอกสารนี้อธิบายการทำงานของระบบในเชิงลำดับเหตุการณ์ (temporal execution)
ไม่ใช่เชิง UI หรือ infrastructure

## 2. Single Correction Lifecycle
1. User emits correction event
2. Event is validated (schema + intent)
3. Affected region is extracted
4. Structural guide is bound to the region
5. Diffusion model executes on scoped input
6. Result is merged into current session state

## 3. Sync vs Async Boundaries
Synchronous:
- Event validation
- Region extraction
- Structural binding

Asynchronous:
- Diffusion execution
- Result delivery
- Logging / metrics

## 4. Atomicity Rules
- A correction batch is atomic
- Partial region failure must not corrupt global state
- Merge step must be idempotent

## 5. Failure Modes (Explicit)
- GPU timeout → event retry or graceful degradation
- Invalid structural guide → reject event
- Stale correction event → drop or rebase
