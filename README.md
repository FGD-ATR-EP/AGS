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
1.  **AetherBus Tachyon**: เส้นทางสั่นพ้องปัญญาที่ลดความหน่วงสู่ระดับไมโครวินาที
2.  **Primary Resonators**: ตำแหน่งผู้สั่นพ้องหลัก 12 ตำแหน่ง (Visionary, Technical, Governance, ฯลฯ)
3.  **Negative Latency**: การทำนายและประมวลผลล่วงหน้า (Ghost Workers) เพื่อให้ AI คิดก่อนที่มนุษย์จะขยับ

---

## 🏛️ สถาปัตยกรรมระดับลึก (Deep Architecture)

ระบบทำงานประสานกันผ่าน **Sopan Protocol**:
`Input (Human Intent) → LogenesisEngine (Formator) → AetherBus (Resonance) → ValidatorAgent (Audit) → AgioSage (Cognitive) → Output (Manifestation)`

### เทคโนโลยีหลัก:
- **FastAPI & WebSockets**: ระบบสื่อสารแบบ Real-time (20Hz Heartbeat)
- **HyperSonicBus**: ระบบส่งข้อมูลความเร็วสูงผ่าน Shared Memory
- **Akashic Records**: บันทึกความจำถาวรแบบ Immutable Ledger (data/akashic_records.json)
- **PWA (Progressive Web App)**: รองรับการติดตั้งและใช้งานเสมือนแอปพื้นฐานบนมือถือและเดสก์ท็อป

### 🗄️ System Architecture Diagram (Database-Centric)

โครงสร้างด้านล่างอ้างอิงจาก schema จริงในโมดูล `src/backend/genesis_core/entropy/` โดยแสดงลำดับข้อมูลจาก `EntropySubmitRequest` → `EntropyPacket`/nested blocks → `EntropyAssessment` และการ persist ลง `EntropyLedgerEntry` ที่ใช้ hash-chain continuity

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
      string hash_prev
      string hash_self
    }
```

**English note:** This diagram mirrors the current entropy schemas and ledger dataclass in code, connecting request payloads (`EntropySubmitRequest` + `EntropyPacket`) to evaluation (`EntropyAssessment`) and immutable persistence (`EntropyLedgerEntry` + hash-chain links).

---


## 🧭 Governance Runtime + Memory Fabric (Engineering Layer)

เพื่อยกระดับจากแนวคิดเชิงวิสัยทัศน์ไปสู่ execution จริง ระบบได้เพิ่ม subsystem แบบ first-class ดังนี้:

- **Governance Core Runtime** (`src/backend/governance/`)
  - Action tiering ระดับ **Tier 0–3**
  - **Policy-as-code** ผ่าน `policy_engine.py`
  - **Approval routing** ผ่าน `approval_router.py`
  - รองรับ recommendation: **quarantine / suspend / rollback**
- **Execution Vessel Layer** (`src/backend/vessels/`)
  - `WorkspaceVessel`, `DriveVessel`, `DatabaseVessel`, `SlackVessel`
  - แนวคิดการทำงาน: **LLM วางแผน → Vessel ลงมือทำ → Governance อนุมัติ → Akashic บันทึก**
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
- **Directive Envelope Standardization**: ทำ schema กลางสำหรับ Intent→Reasoning→Governance→Execution เพื่อให้ trace และ replay ข้ามโมดูลได้เสถียร
- **Governance Dry-Run Mode**: โหมดจำลองผลการอนุมัติ/บล็อกก่อน execute จริง พร้อมเหตุผลและ risk score แบบ explainable
- **Akashic Replay Studio**: UI สำหรับ replay เส้นทางเหตุการณ์ทีละขั้น พร้อม timeline, policy checkpoints และผลกระทบปลายทาง
- **Cross-Vessel Transaction Guard**: กลไก two-phase style approval สำหรับงานที่กระทบหลาย vessel เพื่อลด partial failure
- **Protocol Compatibility Matrix**: ตาราง compatibility ของ packet/schema version เพื่อช่วย rollout แบบ backward compatible
- **Memory Integrity Sentinel**: งานตรวจความครบถ้วน hash-chain + anomaly detection ของ ledger/projections พร้อม alert
- **Observability Pack (OTel-first)**: เพิ่ม trace/span และ governance tags มาตรฐานเพื่อให้ root-cause ได้เร็วขึ้น
- **Policy Simulation Sandbox**: พื้นที่ทดสอบ policy-as-code กับเหตุการณ์สังเคราะห์ก่อน deploy จริง

#### 🇬🇧 New feature and expansion proposals (English)
- **Directive Envelope Standardization** for stable Intent→Reasoning→Governance→Execution tracing and replay across subsystems.
- **Governance Dry-Run Mode** to simulate approve/block decisions before execution, with explainable rationales and risk scores.
- **Akashic Replay Studio** for step-by-step event playback with timeline views, policy checkpoints, and downstream impact visibility.
- **Cross-Vessel Transaction Guard** with two-phase style approvals for multi-vessel operations to reduce partial failures.
- **Protocol Compatibility Matrix** to track packet/schema version interoperability and support backward-compatible rollouts.
- **Memory Integrity Sentinel** to validate hash-chain continuity and detect ledger/projection anomalies with alerting.
- **Observability Pack (OTel-first)** introducing standardized traces/spans and governance tags for faster incident root-cause analysis.
- **Policy Simulation Sandbox** to test policy-as-code behavior against synthetic scenarios prior to production deployment.

---

## 🗺️ เอกสารสำคัญ (Core Documents)
*   [**🇹🇭 USAGE_TH.md**](USAGE_TH.md) - คู่มือการใช้งานภาษาไทย
*   [**📐 TECHNICAL_BLUEPRINT_TH.md**](docs/TECHNICAL_BLUEPRINT_TH.md) - พิมพ์เขียวเชิงเทคนิค
*   [**💼 BUSINESS_PLAN_TH.md**](docs/BUSINESS_PLAN_TH.md) - แผนยุทธศาสตร์ธุรกิจ
*   [**📜 CONSTITUTION.md**](docs/CONSTITUTION.md) - กฎเหล็กของระบบ

---

© 2026 Aetherium Syndicate Inspectra (ASI)
*“Where intelligences resonate, harmony emerges.”*
