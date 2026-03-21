# AI Automation Platform Work Plan (Zapier + AI) — Intent → Workflow ข้ามเครื่องมือ

## 0) Context (CODEX /CREATE_PLATFORM_WORK)
- **Initiative:** Aetherium Cross-Tool AI Automation Platform
- **Scope:** Intent ingestion, planner engine, execution runtime ผ่าน Vessels, intent templates, reusable automations, Akashic ledger audit layer, SRE/Ops controls
- **Drivers:** reliability, latency ที่คาดการณ์ได้, security/compliance, devex สำหรับการเพิ่ม integration ใหม่เร็วขึ้น, ต้นทุนต่อ automation run ต่ำลง
- **Current state (as-is):** มีโครงสร้าง governance, vessel abstraction, และ ledger primitives อยู่แล้ว แต่ยังไม่มี orchestration ที่ครบวงจรจาก intent → plan → execute แบบข้ามเครื่องมือพร้อมมาตรฐาน audit เดียวกัน
- **Target state (to-be):** แพลตฟอร์มที่รับ intent, สร้างแผนงานอัตโนมัติ, dispatch งานไปยังหลายเครื่องมือผ่าน Vessels, รองรับ approval/policy gates และบันทึกทุก event ลง Akashic ledger เพื่อ trace + audit ได้ end-to-end
- **Constraints:**
  - SLO: P95 orchestration latency < 2.5s (plan) และ < 8s (first execution action)
  - Availability: 99.9% สำหรับ orchestration API
  - Budget: จำกัดค่า inference + integration API ต่อ run
  - Timeline: 3 เฟส (12 สัปดาห์)
  - Compliance: auditability, least privilege, data retention policy
- **Dependencies:** ทีม platform/backend, security/compliance, product ops, vendor APIs (Slack/Google Workspace/DB/CRM), LLM provider

---

## 1) Workstreams

### WS1 — Architecture
**เป้าหมาย:** สถาปัตยกรรม Intent-Orchestration ที่แยก concerns ชัดเจน (Trigger, Plan, Execute, Observe, Govern)

- นิยาม service boundaries: `Intent Gateway`, `Planner Service`, `Execution Orchestrator`, `Vessel Connectors`, `Akashic Ledger Writer`, `Policy/Approval Engine`
- กำหนด event model กลางและ correlation IDs สำหรับ trace ข้าม service
- ออกแบบ state machine ของ workflow run (Received → Planned → Approved → Running → Compensating/Completed/Failed)

### WS2 — Protocol
**เป้าหมาย:** มาตรฐานสัญญาข้อมูลสำหรับ intent templates, workflow plans, execution actions

- JSON schema สำหรับ `IntentTemplate`, `WorkflowPlan`, `ActionEnvelope`, `AuditRecord`
- Protocol สำหรับ tool capabilities discovery ผ่าน Vessels
- Versioning strategy (backward compatibility + deprecation windows)

### WS3 — Reliability
**เป้าหมาย:** execution ที่ทนทานต่อ partial failure และปลอดภัย

- Retry/backoff policy ต่อ integration class
- Idempotency keys ต่อ action step
- Circuit breaker + bulkhead isolation สำหรับ connectors
- Compensation actions สำหรับ workflow แบบ transactional-ish

### WS4 — Benchmark
**เป้าหมาย:** baseline และ regression guardrails ของ latency/cost/success rate

- ชุด benchmark scenario: simple/medium/complex cross-tool automations
- วัด metrics: plan accuracy proxy, execution success ratio, P50/P95 latency, cost/run
- กำหนด benchmarking gates ก่อนปล่อย production

### WS5 — Ops
**เป้าหมาย:** readiness เชิงปฏิบัติการ production

- Observability ครบ 3 pillars (logs/metrics/traces)
- Runbooks สำหรับ incident class สำคัญ
- On-call dashboard + alert thresholds
- Key rotation, secret lifecycle, access review cadence

### WS6 — Migration
**เป้าหมาย:** ย้ายจาก flow เดิม/automation scripts เดิมเข้าสู่แพลตฟอร์มใหม่แบบควบคุมความเสี่ยง

- Inventory automation เดิมและจัด tier ตามความ critical
- Canary migration 10% → 30% → 100%
- Dual-run และผล diff เพื่อยืนยันความถูกต้อง

---

## 2) Backlog (Epic → Story → Task + Measurable Acceptance Criteria)

## Epic A: Intent Ingestion & Template System
### Story A1: Intent Template Catalog
- **Task A1.1:** สร้าง schema + validator สำหรับ intent templates
  - **AC:** validator ผ่านกรณีทดสอบอย่างน้อย 50 เคส และ false-positive < 2%
- **Task A1.2:** สร้าง template registry API (CRUD + version)
  - **AC:** รองรับ 200 RPS ที่ p95 < 150ms

### Story A2: Intent Normalization
- **Task A2.1:** สร้าง parser สำหรับ free-text intent → structured goal
  - **AC:** mapping accuracy (golden set) ≥ 90%
- **Task A2.2:** เพิ่ม safety classifier สำหรับ high-risk intents
  - **AC:** high-risk recall ≥ 95%, precision ≥ 85%

## Epic B: Planner Engine (Trigger → Plan)
### Story B1: Plan Synthesis
- **Task B1.1:** พัฒนา planner ที่แปลง intent เป็น DAG workflow
  - **AC:** 95% ของ test intents สร้างแผนที่ executable ได้โดยไม่ต้องแก้มือ
- **Task B1.2:** เพิ่ม tool selection strategy จาก capability metadata
  - **AC:** top-1 tool match accuracy ≥ 92%

### Story B2: Governance Gating
- **Task B2.1:** ผูก policy engine กับ risk tiers
  - **AC:** ทุก workflow run ถูก assign risk tier เสมอ (coverage 100%)
- **Task B2.2:** approval workflow สำหรับ destructive actions
  - **AC:** ไม่มี destructive action ถูก execute โดยไม่มี approval event

## Epic C: Execution Runtime (Plan → Execute ผ่าน Vessels)
### Story C1: Orchestrator Core
- **Task C1.1:** workflow state machine + persistence
  - **AC:** recovery หลัง restart กลับมาทำงานต่อได้ ≥ 99.5%
- **Task C1.2:** step scheduler + dependency resolver
  - **AC:** deadlock = 0 ใน stress test 10k runs

### Story C2: Vessel Connectors
- **Task C2.1:** มาตรฐาน base connector contract
  - **AC:** connector compliance tests ผ่าน 100%
- **Task C2.2:** เพิ่ม connectors อย่างน้อย 4 ตัว (Slack, Workspace, DB, HTTP)
  - **AC:** success rate ต่อ connector ≥ 99% ใน integration test suite

## Epic D: Akashic Ledger Auditability
### Story D1: Unified Audit Event
- **Task D1.1:** สร้าง event envelope เดียวสำหรับทุก phase
  - **AC:** 100% ของ trigger/plan/execute events เขียน ledger ได้สำเร็จ
- **Task D1.2:** tamper-evident chaining (hash link)
  - **AC:** integrity verification job ตรวจผ่านทุกวัน (0 broken chain)

### Story D2: Audit Query & Export
- **Task D2.1:** query API ตาม run_id/user/time/tool
  - **AC:** audit query p95 < 500ms ที่ dataset 10M records
- **Task D2.2:** export รายงาน compliance
  - **AC:** สร้างรายงานรายเดือนอัตโนมัติครบ 100% ของ required controls

## Epic E: Reliability, Benchmark, and Ops Readiness
### Story E1: Reliability Controls
- **Task E1.1:** retries + circuit breaker
  - **AC:** transient failure recovery ≥ 80% โดยไม่ต้อง manual intervention
- **Task E1.2:** compensation workflows
  - **AC:** partial failure ที่ต้อง rollback สำเร็จ ≥ 95%

### Story E2: SLO/Benchmark Gates
- **Task E2.1:** benchmark harness อัตโนมัติใน CI
  - **AC:** benchmark regressions >10% ถูก block release 100%
- **Task E2.2:** SLO burn-rate alerts
  - **AC:** detection time < 5 นาทีใน incident simulation

---

## 3) Options + Tradeoffs + Recommendation

### Option 1: Build-native orchestration engine (in-repo, tightly integrated)
- **Pros:** ควบคุม architecture ได้เต็ม, จูน latency/cost ได้ลึก, ผูก governance/ledger native
- **Cons:** ใช้เวลา dev สูง, maintenance burden เพิ่ม
- **เหมาะเมื่อ:** ต้องการความสามารถเฉพาะ domain และ compliance หนัก

### Option 2: Hybrid (ใช้ workflow engine ภายนอก + custom planner/governance)
- **Pros:** time-to-market เร็ว, ได้ reliability primitives จาก engine สำเร็จรูป, ทีมโฟกัสที่ AI planning + policy
- **Cons:** lock-in บางส่วน, model ของ engine อาจไม่ตรงกับ intent protocol
- **เหมาะเมื่อ:** ต้องการ shipping เร็วแต่ยังรักษาจุดต่างด้าน intelligence/governance

### Option 3: iPaaS-first (ใช้ Zapier/Make เป็น execution backbone)
- **Pros:** เร็วที่สุดในการเริ่ม, integration สำเร็จรูปจำนวนมาก
- **Cons:** control/observability/compliance จำกัด, latency & cost คุมยาก, custom logic ลึกทำได้จำกัด
- **เหมาะเมื่อ:** MVP เชิงธุรกิจระยะสั้น

## Recommendation (เลือก Option 2)
เลือก **Hybrid** เพราะบาลานซ์ดีที่สุดระหว่างความเร็วและการควบคุม:
1) ใช้ engine ภายนอกรับภาระ retry/state/replay พื้นฐาน,
2) วาง `Planner + Governance + Akashic Ledger` เป็น core differentiator ภายใน,
3) ลดระยะส่งมอบเฟสแรกโดยไม่เสียมาตรฐาน audit.

---

## 4) Risks, Failure Modes, Mitigation
- **Risk:** Intent misinterpretation ทำให้รัน action ผิดบริบท
  - **Failure mode:** planner เลือก tool/step ไม่ตรงเจตนา
  - **Mitigation:** human-in-the-loop สำหรับ risk tier สูง + semantic validation ก่อน execute

- **Risk:** Partial failure ข้ามหลายระบบ
  - **Failure mode:** ระบบ A สำเร็จแต่ระบบ B ล้มเหลว ทำให้ข้อมูลไม่สอดคล้อง
  - **Mitigation:** compensation playbooks, idempotency keys, saga-like rollback design

- **Risk:** Connector API change ไม่เข้ากัน
  - **Failure mode:** execution fail กระทันหันหลัง vendor update
  - **Mitigation:** contract tests รายวัน + version pinning + canary connectors

- **Risk:** Audit gaps
  - **Failure mode:** บาง event ไม่ถูกบันทึกลง ledger
  - **Mitigation:** write-ahead audit queue + reconciliation jobs + missing-event alerts

- **Risk:** Cost overrun จาก LLM planning
  - **Failure mode:** ต้นทุนต่อ run สูงเกิน budget
  - **Mitigation:** model routing ตาม complexity, caching plan fragments, budget guardrail per tenant

---

## 5) Rollout / Rollback Plan (Owner + Timeline)

## Phase 0 (สัปดาห์ 1-2): Foundations
- **Owner:** Platform Architect + Lead Backend
- ส่งมอบ protocol schemas, baseline architecture, risk model
- **Gate:** design review sign-off + security review pass

## Phase 1 (สัปดาห์ 3-6): Core Planner + Ledger + 2 Connectors
- **Owner:** Orchestration Team
- ส่งมอบ Trigger→Plan→Execute (limited), Akashic audit end-to-end, Slack/HTTP connectors
- **Gate:** 95% core e2e tests ผ่าน, audit coverage 100%

## Phase 2 (สัปดาห์ 7-10): Reliability + Ops + Expansion
- **Owner:** SRE + Integrations Team
- เพิ่ม retry/circuit breaker/compensation, dashboards/runbooks, connectors เพิ่มเติม
- **Gate:** SLO simulation ผ่าน, incident game day ผ่าน

## Phase 3 (สัปดาห์ 11-12): Migration + Production Cutover
- **Owner:** Product Ops + Platform
- dual-run, canary rollout, full cutover
- **Gate:** error budget stable 2 สัปดาห์, rollback drills ผ่าน

### Rollback Strategy
- Feature flags ต่อ workflow family
- Canary isolation ต่อ tenant/group
- Snapshot/restore state store ก่อน cutover
- ถ้า SLO breach ต่อเนื่อง > 30 นาที: auto fallback ไป legacy route

---

## 6) Definition of Done (Production-grade)

### Tests
- Unit coverage โมดูลสำคัญ ≥ 85%
- Contract tests สำหรับทุก connector + protocol version
- E2E tests ครอบคลุมเส้นทางหลักและ failure paths

### SLO Gates
- Orchestration API availability ≥ 99.9%
- Plan latency p95 < 2.5s
- First action latency p95 < 8s
- Workflow success rate ≥ 98%

### Benchmarking Gates
- ไม่มี regression latency/cost เกิน 10% เมื่อเทียบ baseline release ล่าสุด
- Planner quality score (golden set) ≥ 90%

### Observability
- Distributed tracing ด้วย correlation ID ทุก run
- Structured logs สำหรับทุก state transition
- Dashboard + burn-rate alerts + anomaly alerts

### Runbooks
- Incident runbooks: planner outage, connector degradation, ledger lag, approval queue backlog
- Recovery drills รายไตรมาส

### Security Checks
- Secrets rotation ≤ 90 วัน
- Least-privilege scopes สำหรับ connectors
- Static analysis + dependency vulnerability scan ผ่านระดับที่กำหนด
- Audit trail completeness checks รายวัน

---

## 7) Architecture / Protocol Update Outline
1. เพิ่ม `Intent Gateway` API และ template registry
2. เพิ่ม `Planner Service` ที่สร้าง executable DAG
3. เพิ่ม `Execution Orchestrator` state machine + scheduler
4. ขยาย `Vessel` contract ให้รองรับ capability discovery, idempotency, compensation
5. ขยาย `Akashic Ledger` schema ให้รองรับ event ชุดใหม่ (trigger/plan/execute/approval/compensation)
6. ผูก `Governance Engine` กับ risk tier + approval policy
7. เพิ่ม telemetry มาตรฐานเดียวทั้งระบบ

---

## 8) Reliability & Ops Readiness Checklist
- [ ] SLOs ถูก define และ monitor จริงใน production
- [ ] Alert routing + on-call ownership ครบทุก critical service
- [ ] Runbooks ถูกทดสอบใน game day ล่าสุด
- [ ] Connector contract tests รันอัตโนมัติรายวัน
- [ ] Ledger reconciliation job มีรายงานผลและ alert
- [ ] Backup/restore ทดสอบแล้วในสภาพแวดล้อม staging
- [ ] Security review + threat model update ผ่าน
- [ ] Rollback drills ผ่านตามเกณฑ์เวลา RTO/RPO
