# Internal Audit + Reward Integrity + Intent Intelligence Work Plan

## 0) Context (CODEX /CREATE_PLATFORM_WORK)
- **Initiative:** Ledger-Driven Integrity Platform for Audit, Rewards, and Cross-Session Intent Detection
- **Scope:** services (`ledger-explorer-api`, `reward-guardrails`, `intent-graph-service`), protocol/schema, observability pipeline, ops runbooks, migration path
- **Drivers:** reliability, security/compliance, anti-gaming protection, lower fraud-loss cost, devex for risk-team analytics
- **Current state (as-is):** มี ledger records และ session-level telemetry อยู่แล้ว แต่ยังขาด API สำหรับ audit query แบบ time-range/QoU, ขาด dynamic reward controls, และยัง correlate intent ได้แค่ session เดียว
- **Target state (to-be):** มี API ตรวจสอบ ledger ระดับ audit-ready พร้อม hash-chain continuity checks, มีกลไก Adaptive Reward Guardrails ปรับเพดาน/พื้นรางวัลตามความเสี่ยงแบบเรียลไทม์, และมี Cross-Session Intent Graph สำหรับจับ long-horizon anomaly
- **Constraints:**
  - SLO: Explorer API P95 < 300ms (cached) / < 900ms (cold query)
  - Risk gate latency: < 80ms ต่อ reward decision
  - Timeline: 3 phases / 10 สัปดาห์
  - Compliance: immutable audit trail, retention 18 เดือน, policy explainability
  - Budget: เพิ่ม infra cost ไม่เกิน 20% จาก baseline telemetry stack
- **Dependencies:** Platform backend, Risk/Trust & Safety, Data engineering, Security, Internal audit stakeholders

---

## 1) Workstreams

### WS1 — Architecture
- แยก bounded context: `Ledger Explorer`, `Reward Risk Engine`, `Intent Graph`
- ออกแบบ shared IDs (`entity_id`, `session_id`, `packet_id`, `chain_id`) และ event-time semantics
- นิยาม data flow: ingest → normalize → feature compute → decision/query surfaces

### WS2 — Protocol
- เพิ่ม schema: `LedgerQueryRequest`, `QoUBand`, `HashContinuityReport`, `RewardGuardrailDecision`, `IntentEdge`
- กำหนด versioning strategy แบบ additive-first + deprecation 2 releases
- กำหนด policy reason-codes เพื่อ explainability ต่อ audit

### WS3 — Reliability
- Hash-chain verifier job แบบ incremental + replay-safe
- Reward decision fallback policy (safe floor/ceiling defaults) เมื่อ feature store ล่ม
- Graph build pipeline แบบ exactly-once semantic (idempotent upsert edges)

### WS4 — Benchmark
- Benchmark ชุด query pattern (hot/cold, narrow/wide time-range)
- Stress test reward decision path ที่ 1k/5k/10k RPS
- Graph anomaly detection quality benchmark (precision/recall/FPR)

### WS5 — Ops
- Dashboard แยก 3 มุม: audit query health, reward-risk pressure, graph anomaly trends
- Alerting: hash gap spikes, guardrail override rate, intent anomaly surge
- Runbooks: data lag, continuity break, false-positive burst, rollback guardrails

### WS6 — Migration
- Dual-write จาก ledger เดิมไป schema ใหม่
- Shadow mode สำหรับ reward guardrails (observe-only)
- Parallel scoring สำหรับ intent graph ก่อนเปิด enforcement

---

## 2) Backlog (Epic → Story → Task + Measurable AC)

## Epic A: Ledger Explorer API for Internal Audit
### Story A1: Time-range and QoU filtering
- **Task A1.1:** สร้าง endpoint `GET /ledger/events` รองรับ `from_ts`, `to_ts`, `entity`, `qou_band`
  - **AC:** query ช่วงเวลา 7 วันบน 50M events ได้ P95 < 900ms
- **Task A1.2:** เพิ่ม index/materialized view สำหรับ QoU bands
  - **AC:** query ด้วย QoU filter เร็วขึ้นอย่างน้อย 40% เทียบ baseline

### Story A2: Hash-chain continuity checks
- **Task A2.1:** สร้าง endpoint `GET /ledger/continuity-report`
  - **AC:** ตรวจพบ missing-link/tamper simulation ได้ 100% ใน test fixtures
- **Task A2.2:** เพิ่ม scheduled verifier + reconciliation log
  - **AC:** ครอบคลุม chain verification ≥ 99.99% ของ daily appended records

### Story A3: Internal audit workflow integration
- **Task A3.1:** เพิ่ม export `CSV/JSON signed bundle`
  - **AC:** export พร้อม signature verification ผ่าน 100% ใน audit test suite
- **Task A3.2:** เพิ่ม RBAC scope `audit.read`, `audit.export`
  - **AC:** unauthorized access blocked 100% ใน authorization tests

## Epic B: Adaptive Reward Guardrails
### Story B1: Dynamic floor/ceiling engine
- **Task B1.1:** สร้าง risk-score adapter จาก behavior features (velocity, repetition entropy, dispute rate)
  - **AC:** feature freshness lag < 2 นาที ใน 99% ของ events
- **Task B1.2:** สร้าง policy function ปรับ reward floor/ceiling ตาม risk tier
  - **AC:** ลด outlier reward payouts ≥ 30% โดยไม่ลด median legitimate reward เกิน 5%

### Story B2: Anti-gaming pressure controls
- **Task B2.1:** เพิ่ม dampening logic ต่อ pattern ที่เสี่ยง farming
  - **AC:** farming-success ratio ลดลง ≥ 40% ใน adversarial simulation
- **Task B2.2:** เพิ่ม override + human review queue สำหรับ borderline cases
  - **AC:** manual override SLA < 15 นาที (P95)

### Story B3: Policy transparency
- **Task B3.1:** บันทึก `decision_trace` และ reason-codes ต่อ reward event
  - **AC:** explainability coverage 100% ของ sampled reward decisions

## Epic C: Cross-Session Intent Graph
### Story C1: Graph ingestion and stitching
- **Task C1.1:** สร้าง packet-to-intent edge builder ข้าม session ด้วย identity linkage confidence
  - **AC:** edge creation throughput ≥ 20k edges/sec โดย data loss = 0
- **Task C1.2:** สร้าง horizon windows (1h/24h/7d/30d)
  - **AC:** query intent trajectory ได้ภายใน 1.2s (P95)

### Story C2: Long-horizon anomaly surfacing
- **Task C2.1:** พัฒนา detectors (motif repetition, escalation chains, delayed exploit intent)
  - **AC:** precision ≥ 0.88, recall ≥ 0.82 บน labeled validation set
- **Task C2.2:** เพิ่ม analyst API สำหรับ reason graph retrieval
  - **AC:** analyst resolve time ลดลง ≥ 25% เทียบ process เดิม

### Story C3: Cross-system actionability
- **Task C3.1:** เชื่อม anomaly output กับ reward guardrail risk tier
  - **AC:** high-risk intent signals ถูกสะท้อนใน guardrail decision ภายใน 3 นาที

---

## 3) Options + Tradeoffs + Recommendation

### Option 1: Monolithic Integrity Service
- **Pros:** operational surface น้อย, deployment ง่าย
- **Cons:** blast radius สูง, scale แยก workload ยาก (query vs scoring vs graph)

### Option 2: Event-driven microservices + shared schema registry
- **Pros:** scale แยกตาม domain, fault isolation ดี, evolve protocol ได้ชัด
- **Cons:** complexity สูงขึ้น (orchestration, schema governance, tracing)

### Option 3: Data-warehouse-first analytics + thin online controls
- **Pros:** dev เร็วในช่วงแรก, analyst productivity ดี
- **Cons:** latency สูง ไม่เหมาะกับ reward guardrails แบบ near-real-time

## Recommendation: **Option 2**
เลือก event-driven microservices เพราะรองรับทั้ง low-latency decisioning และ deep audit/analytics พร้อมกัน และลดความเสี่ยงจาก single-point-of-failure ของระบบเดียวขนาดใหญ่

---

## 4) Risks, Failure Modes, Mitigation
- **Risk:** Hash continuity false alarm สูงจาก out-of-order ingestion
  - **Failure mode:** alert ล้นจนทีม ignore
  - **Mitigation:** watermark + lateness window + two-phase continuity verdict

- **Risk:** Reward guardrails กระทบผู้ใช้ดีเกินไป (false positive)
  - **Failure mode:** engagement/revenue drop
  - **Mitigation:** shadow mode, capped impact rollout, per-segment calibration

- **Risk:** Identity stitching ผิด ทำให้ graph ผิดบริบท
  - **Failure mode:** investigator ตัดสินใจผิด
  - **Mitigation:** confidence threshold + uncertainty labeling + manual merge/split tools

- **Risk:** Feature store lag
  - **Failure mode:** decision stale
  - **Mitigation:** freshness SLO monitor + fail-safe static policy fallback

- **Risk:** Protocol drift ข้ามทีม
  - **Failure mode:** downstream parse fail
  - **Mitigation:** schema contract tests ใน CI + compatibility checker gate

---

## 5) Rollout / Rollback Plan (Owner + Timeline)

### Phase 1 (Week 1-3): Foundations + Explorer API MVP
- **Owner:** Platform API Lead
- Deliver: query API time-range/QoU + basic continuity report
- **Gate:** load test ผ่าน, RBAC/security tests ผ่าน
- **Rollback:** route traffic กลับ read replica เดิมผ่าน API gateway flag

### Phase 2 (Week 4-7): Adaptive Reward Guardrails (Shadow → Limited Enforce)
- **Owner:** Risk Engine Lead
- Deliver: dynamic floors/ceilings + decision trace + review queue
- **Gate:** shadow precision/recall ถึง target, business KPI ไม่ถดถอยเกิน guardband
- **Rollback:** กลับ static reward policy ทันทีผ่าน feature flag ภายใน 5 นาที

### Phase 3 (Week 8-10): Cross-Session Intent Graph + Integrated Controls
- **Owner:** Data Intelligence Lead
- Deliver: cross-session graph + anomaly API + coupling สู่ reward tiers
- **Gate:** detection quality ถึงเกณฑ์, incident drill ผ่าน
- **Rollback:** ปิด graph-driven signals แล้วคง rule-based risk path ต่อได้โดยไม่ downtime

---

## 6) Definition of Done (Production)

### Tests
- Unit test coverage ≥ 85% สำหรับ core policy/query logic
- Contract tests ครบทุก schema/event versions
- E2E tests สำหรับ 3 เส้นทางหลัก: audit export, reward decision, anomaly surfacing

### SLO Gates
- Explorer API availability ≥ 99.9%
- Reward decision P95 < 80ms
- Graph ingestion lag P95 < 120s

### Benchmarking Gates
- Query throughput ≥ 2k QPS (mix workload) โดย P95 ไม่เกิน target
- Reward engine sustain 5k RPS พร้อม error rate < 0.2%
- Anomaly detector regression ไม่เกิน -3% precision หรือ -3% recall

### Observability
- Metrics ครบ: request latency, continuity gap rate, guardrail impact %, anomaly volume
- Distributed tracing cross-service พร้อม correlation IDs
- Structured logs ที่มี reason-codes สำหรับ audit replay

### Runbooks
- Runbook incident class: continuity break, false-positive spike, data lag, schema break
- On-call playbook พร้อม escalation matrix และ MTTR target

### Security Checks
- RBAC + least privilege review รายไตรมาส
- Signed audit exports + key rotation policy
- Dependency + container vulnerability scans block critical CVEs
