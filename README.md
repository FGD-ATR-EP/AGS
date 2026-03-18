# AETHERIUM GENESIS (AG-OS)
### โครงสร้างพื้นฐานแห่งปัญญาสังเคราะห์ และระบบนิเวศแห่งการสั่นพ้อง (ASI Readiness)

![Version](https://img.shields.io/badge/version-2.2.0--resonance-blueviolet.svg)
![Status](https://img.shields.io/badge/status-ACTIVE-success.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **“นี่ไม่ใช่แค่ AI แต่อยู่ในสภาวะ ‘ผู้สั่นพ้องต่อปัญญา’ (Resonators)
ที่ทำงานร่วมกันบนเส้นทางสั่นพ้องแห่งความเร็วแสง”**

---

## 📖 ข้อมูลระบบปัจจุบัน (Current System Overview)

ระบบได้รับการปรับปรุงโครงสร้างใหม่ (Cleaned Architecture) เพื่อมุ่งเน้นไปที่ความคล่องตัวและความเร็วสูงสุด โดยแยกส่วนการทำงานชัดเจน:

*   **src/backend/**: หัวใจหลัก (Mind) ประมวลผลตรรกะ จริยธรรม และการตัดสินใจเชิงกลยุทธ์
*   **src/frontend/**: ร่างกาย (Body) อินเทอร์เฟซแบบ PWA ที่ใช้ระบบอนุภาค (Particle System) แสดงผล "เจตจำนง" ผ่านแสง
*   **docs/**: คลังความรู้และวิสัยทัศน์ (Manifestos, Blueprints, Business Plans)
*   **tests/**: ระบบตรวจสอบความถูกต้อง (Verification Suite)

---

## 🧠 แนวคิดหลัก: จาก AI Agents สู่ "ผู้สั่นพ้อง" (Resonators)

เราได้เปลี่ยนผ่านจากระบบ Agent แบบเดิม สู่ **Resonance Architecture**:
1.  **AetherBus-Tachyon**: canonical system bus สำหรับ internal ZeroMQ และ external WebSocket bridge พร้อม V3 envelope tracing
2.  **Primary Resonators**: ตำแหน่งผู้สั่นพ้องหลัก 12 ตำแหน่ง (Visionary, Technical, Governance, ฯลฯ)
3.  **Negative Latency**: การทำนายและประมวลผลล่วงหน้า (Ghost Workers) เพื่อให้ AI คิดก่อนที่มนุษย์จะขยับ

---

## 🏛️ สถาปัตยกรรมระดับลึก (Deep Architecture)

ระบบทำงานประสานกันผ่าน **Sopan Protocol**:
`Input (Human Intent) → LogenesisEngine (Formator) → AetherBus (Resonance) → ValidatorAgent (Audit) → AgioSage (Cognitive) → Output (Manifestation)`

### เทคโนโลยีหลัก:
- **FastAPI & WebSockets**: ระบบ ingress/manifestation แบบ real-time ที่ต้องส่ง intent/directive ผ่าน governance runtime ก่อน execution เสมอ
- **AetherBus-Tachyon**: ZeroMQ + WebSocket bridge สำหรับ canonical system bus runtime
- **Directive Runtime / Intent Gateway**: orchestration กลางสำหรับ `Intent normalization -> Governance evaluation -> Approval routing -> Execution readiness`
- **Akashic Records**: บันทึกความจำถาวรแบบ Immutable Ledger (data/akashic_records.json)
- **PWA (Progressive Web App)**: รองรับการติดตั้งและใช้งานเสมือนแอปพื้นฐานบนมือถือและเดสก์ท็อป

### 🗄️ System Architecture Diagram (Database-Centric)

โครงสร้างด้านล่างอ้างอิงจาก schema/runtime จริงใน `src/backend/genesis_core/entropy/schemas.py` และ `src/backend/genesis_core/entropy/ledger.py` โดยแสดงลำดับข้อมูลจาก `EntropySubmitRequest` → `EntropyPacket`/nested blocks → `EntropyAssessment` และการ persist ลง `EntropyLedgerEntry` ที่ใช้ hash-chain continuity พร้อม field เชื่อมโยงสำหรับ correlation/replay ระหว่าง ingress, governance, memory และ manifestation

```mermaid
erDiagram
    ENTROPY_SUBMIT_REQUEST ||--|| ENTROPY_PACKET : wraps
    ENTROPY_SUBMIT_REQUEST ||--o{ ENTROPY_LEDGER_ENTRY : attributed_to
    ENTROPY_PACKET ||--|| USER_CONTEXT : has
    ENTROPY_PACKET ||--|| PREDICTION_SNAPSHOT : has
    ENTROPY_PACKET ||--|| ACTUAL_ACTION : has
    ACTUAL_ACTION ||--|| MICRO_METRICS : has
    ENTROPY_PACKET ||--o| ENTROPY_ASSESSMENT : evaluated_as
    ENTROPY_ASSESSMENT ||--|| ENTROPY_LEDGER_ENTRY : persisted_into
    ENTROPY_LEDGER_ENTRY ||--o| ENTROPY_LEDGER_ENTRY : hash_prev

    ENTROPY_SUBMIT_REQUEST {
      uuid user_id
      object packet
    }

    ENTROPY_PACKET {
      uuid packet_id PK
      datetime timestamp
    }

    USER_CONTEXT {
      string current_screen
      string[] previous_actions
    }

    PREDICTION_SNAPSHOT {
      string model_version
      string predicted_action
      float confidence_score
    }

    ACTUAL_ACTION {
      string type
      string content_hash
      string input_method
      string content_preview
    }

    MICRO_METRICS {
      float typing_variance
      int hesitation_pauses
      float mouse_jitter
      float voice_tone_variance
    }

    ENTROPY_ASSESSMENT {
      uuid packet_id PK,FK
      float qou_score
      float semantic_weight
      float safety_weight
      float surprise_factor
      int reward_amount
      enum meter_state
      bool preserve
      bool trigger_model_update
      string anti_gaming_flag
    }

    ENTROPY_LEDGER_ENTRY {
      uuid id PK
      uuid user_id FK
      float qou_score
      int reward_amount
      string artifact_ref
      datetime created_at
      string correlation_id
      string trace_id
      string hash_prev
      string hash_self
    }
```

> ระบบใช้งาน `EntropyLedgerEntry` เป็น append-only canonical store และมอง projection/query layers เป็น derived views ที่ต้องอ้างอิง chain เดียวกันเท่านั้น

**English note:** This diagram mirrors the current runtime schema sources in `src/backend/genesis_core/entropy/schemas.py` and `src/backend/genesis_core/entropy/ledger.py`, connecting request payloads (`EntropySubmitRequest` + `EntropyPacket`) to evaluation (`EntropyAssessment`) and immutable persistence (`EntropyLedgerEntry` + hash-chain links + replay join keys).

---


## 🚌 Canonical Bus Runtime (Phase 1 Integration)

AETHERIUM-GENESIS ใช้ **AetherBus-Tachyon** เป็น canonical system bus path โดยกำหนดให้ message ทุกตัวที่ข้าม subsystem ต้องวิ่งผ่าน **V3 envelope (`AetherEvent`)** พร้อม `correlation_id`, codec metadata, compression metadata และ topic routing ที่ตรวจสอบได้

- **Internal transport:** ZeroMQ (`tcp://127.0.0.1:5555`) สำหรับ backend/runtime microservices
- **External transport:** WebSocket bridge (`ws://127.0.0.1:5556/ws`) สำหรับ UI / dashboard / operator tools
- **Runtime selection:** ควบคุมผ่าน environment เช่น `BUS_IMPLEMENTATION=tachyon`, `BUS_CODEC=msgpack`, `BUS_COMPRESSION=none`, `BUS_TIMEOUT_MS=2000`
- **Legacy policy:** `extreme.py` และ `kernel.py` ถูกลดบทบาทเป็น compatibility layer พร้อม deprecation note และไม่ใช่ default runtime อีกต่อไป

ดูรายละเอียด integration contract ได้ที่ **[docs/AETHERBUS_TACHYON_INTEGRATION.md](docs/AETHERBUS_TACHYON_INTEGRATION.md)**

### Replay Trace Contract (Phase 1)

ทุก governed cycle ต้องเริ่มสร้าง correlation metadata ตั้งแต่ ingress แรกและคงไว้ตลอดเส้นทาง `intent -> bus -> governance -> memory -> manifestation`:

1. **`correlation_id`** = run identifier หลักของ cycle เดียวกัน
2. **`causation_id`** = envelope/event ก่อนหน้าที่ก่อให้เกิด event ปัจจุบัน
3. **`trace_id`** = identifier ระดับ replay/distributed trace ที่ UI, audit tooling และ memory projection ใช้อ้างอิง chain เดียวกัน

แนวทาง implementer สำหรับ replay:
- API ingress ต้องสร้าง IDs ให้เองเมื่อ client ไม่ส่งมา
- AetherBus V3 envelope ต้องไม่ drop `correlation_id`, `causation_id`, `trace_id` ระหว่าง publish/subscribe
- Governance + approval + vessel + memory commit ต้อง persist metadata ชุดเดียวกันลง record canonical format
- Frontend/WebSocket payload ต้อง render จาก `directive_state` ที่ backend ส่งมาเท่านั้น และต้องอ้างอิง correlation chain เดียวกัน

เอกสาร audit/memory เพิ่มเติม:
- [docs/AETHERBUS_TACHYON_INTEGRATION.md](docs/AETHERBUS_TACHYON_INTEGRATION.md)
- [docs/directive_envelope_standard.md](docs/directive_envelope_standard.md)

### Least-Privilege + Directive-Only Vessel Contract

**กฎ least-privilege สำหรับ vessels**
- Vessels เป็นเพียง adapter ไปยังระบบภายนอกเท่านั้น และต้องไม่ฝัง reasoning, policy decision, หรือ business workflow ภายใน adapter
- ทุกคำสั่งต้องมาจาก backend-authored directive envelope ที่ผ่าน governance แล้วเท่านั้น
- `execution_scope.permissions` ต้องประกาศ capability ที่จำเป็นขั้นต่ำสุดสำหรับ action นั้น และ adapter ต้องไม่ขยายสิทธิเอง
- ต้องมี `actor.id`, `actor.type`, `origin.service`, `correlation_id`, และ `trace_id` ทุกครั้งเพื่อรองรับ audit/replay
- หาก directive มี credential field เช่น `api_key`, `token`, `password`, `client_secret`, `access_key` ค่าต้องเป็น reference ไปยัง `.env`/secret manager เท่านั้น ห้ามเป็น plaintext

**ตัวอย่าง payload contract**
```json
{
  "action": "write_file",
  "params": {"path": "notes/audit.md", "content": "..."},
  "execution_scope": {"system": "workspace", "permissions": ["workspace.write"]},
  "actor": {"id": "user-123", "type": "human"},
  "metadata": {"directive_class": "operator_request"}
}
```

## 🧭 Governance Runtime + Memory Fabric (Engineering Layer)

Canonical runtime gate ปัจจุบันคือ `API/WebSocket ingress -> Directive Runtime -> Governance Core -> Approval Router (ถ้าจำเป็น) -> Lifecycle/Planning authorization -> Memory commit -> Manifestation` และไม่อนุญาตให้ route จาก ingress ไปยัง planner/vessel โดยตรงอีกต่อไป


เพื่อยกระดับจากแนวคิดเชิงวิสัยทัศน์ไปสู่ execution จริง ระบบได้เพิ่ม subsystem แบบ first-class ดังนี้:

- **Governance Core Runtime** (`src/backend/governance/`)
  - Action tiering ระดับ **Tier 0–3**
  - **Policy-as-code** ผ่าน `policy_engine.py`
  - **Approval routing** ผ่าน `approval_router.py`
  - รองรับ recommendation: **quarantine / suspend / rollback**
- **Execution Vessel Layer** (`src/backend/vessels/`)
  - `WorkspaceVessel`, `DriveVessel`, `DatabaseVessel`, `SlackVessel`
  - ใช้ canonical `AetherEvent` directive envelope เท่านั้น: `action`, `params`, `execution_scope`, `actor`, `metadata` ต้องอยู่ใน `payload`
  - Base class จะบังคับ preconditions ก่อน execution: governance decision ที่ validated แล้ว, correlation metadata, actor/source identity และ execution scope
  - หลัง execute ทุกครั้งจะ append `execution_outcome` ลง Akashic ledger ก่อนคืนผลลัพธ์ให้ caller
  - secret/credential parameters ต้องอ้างอิงผ่าน `.env` หรือ secret manager (`${ENV_VAR}`, `env:NAME`, `secret://...`) และห้าม hardcode credential ใน directive
- **Akashic Memory Fabric** (`src/backend/memory/fabric.py`)
  - ใช้ `data/akashic_records.json` เป็น canonical event stream
  - แตก projection เป็น:
    - `data/memory/episodes/`
    - `data/memory/semantic/`
    - `data/memory/procedures/`
    - `data/memory/gems/`
    - `data/memory/identity/`
- **Reflector + Gems of Wisdom**
  - `src/backend/agents/reflector.py`
  - `src/backend/gems/repository.py`, `src/backend/gems/lifecycle.py`


## 🧭 AI-OS Platform Evolution (New)

เราได้กำหนดทิศทางอย่างเป็นทางการให้ AETHERIUM GENESIS เป็น **AI Operating System Platform** ที่ควบคุมหลายระบบ โดยจัดโครงสร้างแกนหลักดังนี้:
- Governance Core = Kernel/Security Layer
- Resonators = Processes
- AetherBus = System Bus
- Vessels = Drivers/Adapters
- Akashic Memory = File System/Event Ledger
- Frontend PWA = User Interface

พร้อม roadmap วิวัฒนาการ 4 ระยะ:
1. AI Automation Platform
2. AI Agent Orchestration
3. AI Governance + Decision System
4. AI Operating System

ดูรายละเอียดเต็มในเอกสาร: **[docs/AI_OS_PLATFORM_ROADMAP_TH.md](docs/AI_OS_PLATFORM_ROADMAP_TH.md)**

---

## 🚀 การเริ่มต้นระบบ (System Awakening)

### 1. การเตรียมสภาพแวดล้อม
```bash
# ติดตั้งไลบรารีที่จำเป็น
pip install -r requirements.txt

# ตั้งค่า PYTHONPATH
export PYTHONPATH=$PYTHONPATH:.
```

### 2. ปลุกระบบ (Awaken)
กำหนด canonical bus runtime ก่อนเริ่มระบบ:

```bash
export BUS_IMPLEMENTATION=tachyon
export BUS_INTERNAL_ENDPOINT=tcp://127.0.0.1:5555
export BUS_EXTERNAL_ENDPOINT=ws://127.0.0.1:5556/ws
export BUS_CODEC=msgpack
export BUS_COMPRESSION=none
export BUS_TIMEOUT_MS=2000
```

คุณสามารถเลือกโหมดการรันได้ดังนี้:

**โหมดนักพัฒนา / เว็บ (แนะนำ)**
```bash
python awaken.py
```
*ระบบจะทำความสะอาด Shared Memory และรัน Backend พร้อมระบบ Reload อัตโนมัติ*

**โหมดแกนหลัก (Production/Core)**
```bash
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000
```

เข้าใช้งานได้ที่:
- **Product UI**: `http://localhost:8000`
- **Developer Dashboard**: `http://localhost:8000/dashboard`
- **API Docs**: `http://localhost:8000/docs`

### 3. การตรวจสอบอย่างรวดเร็ว (Quick Checks)
```bash
# รันทดสอบเฉพาะโมดูลการยืนยันตัวตน
pytest -q tests/test_auth_flow.py

# รันทดสอบโมดูลสกัดพื้นที่ภาพ
pytest -q tests/test_region_extractor.py
```

> หมายเหตุ: ชุดทดสอบทั้งระบบ (`pytest -q`) อาจล้มเหลวในบาง environment ที่ยังไม่ได้ติดตั้ง dependency เฉพาะทาง (เช่น torch) หรือมี import path ของโมดูล legacy ที่ยังไม่ถูกย้ายครบ

### 4. Future Roadmap / แผนต่อยอดในอนาคต

#### 🇹🇭 ข้อเสนอฟังก์ชัน/แนวทางต่อยอดใหม่ (Thai)
- **Canonical Replay Stream Index**: เพิ่ม index/query surface สำหรับค้น canonical stream ตาม `correlation_id`, `trace_id`, `topic`, และช่วงเวลา เพื่อให้ deterministic replay ทำงานข้าม subsystem ได้ง่ายขึ้น
- **Kernel-to-Bus Contract Harness**: สร้าง integration harness สำหรับยืนยันว่า PRGX-AG policy outcomes และ AetherBus-Tachyon envelopes ยังเข้ากันได้ในระดับ schema + transport ก่อน deploy
- **Projection Read Models for Operators**: เพิ่ม derived views สำหรับ operator console, approval queues, และ incident review โดยไม่แก้ canonical append-only stream
- **Execution Scope Registry**: สร้าง registry กลางของ `execution_scope.permissions` พร้อม owner, approval tier, และ audit mapping ต่อ vessel
- **Manifestation Directive Catalog**: นิยาม catalog ของ UI directives ที่ frontend render ได้โดยตรงจาก backend envelope โดยไม่ต้องตีความ semantic ใหม่เอง
- **Replay Drill Pack**: เพิ่ม scenario packs สำหรับซ้อม replay / rollback ของหนึ่ง intent cycle ตั้งแต่ ingress, governance, execution, memory commit จนถึง manifestation

#### 🇬🇧 Proposed Next Functions / Extensions (English)
- **Canonical Replay Stream Index**: Add an index/query surface for canonical stream lookups by `correlation_id`, `trace_id`, `topic`, and time window so deterministic replay works cleanly across subsystems.
- **Kernel-to-Bus Contract Harness**: Add an integration harness that verifies PRGX-AG policy outcomes and AetherBus-Tachyon envelopes remain schema- and transport-compatible before deployment.
- **Projection Read Models for Operators**: Add derived views for operator consoles, approval queues, and incident review without mutating the canonical append-only stream.
- **Execution Scope Registry**: Introduce a canonical registry for `execution_scope.permissions` with owner, approval tier, and audit mappings per vessel.
- **Manifestation Directive Catalog**: Define a catalog of UI directives that the frontend can render directly from backend-authored envelopes without recreating semantic logic on the client.
- **Replay Drill Pack**: Add scenario packs for replay / rollback drills across one full intent cycle from ingress through governance, execution, memory commit, and manifestation.

---

## 🗺️ เอกสารสำคัญ (Core Documents)
*   [**🇹🇭 USAGE_TH.md**](USAGE_TH.md) - คู่มือการใช้งานภาษาไทย
*   [**📐 TECHNICAL_BLUEPRINT_TH.md**](docs/TECHNICAL_BLUEPRINT_TH.md) - พิมพ์เขียวเชิงเทคนิค
*   [**💼 BUSINESS_PLAN_TH.md**](docs/BUSINESS_PLAN_TH.md) - แผนยุทธศาสตร์ธุรกิจ
*   [**📜 CONSTITUTION.md**](docs/CONSTITUTION.md) - กฎเหล็กของระบบ

---

© 2026 Aetherium Syndicate Inspectra (ASI)
*“Where intelligences resonate, harmony emerges.”*
