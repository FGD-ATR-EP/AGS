# ระบบเศรษฐศาสตร์เอนโทรปี (Entropy Economy Technical Specification)

- **Project:** AETHERIUM GENESIS (Module: AetherBusExtreme / CSP-X1)
- **Version:** 1.0 Alpha
- **Status:** Confidential Blueprint

## 1) วัตถุประสงค์ (Purpose)

ระบบนี้ออกแบบมาเพื่อสร้างมูลค่าจาก "ความไม่แน่นอนของมนุษย์" (Human Entropy) โดยวัดระยะห่างระหว่างสิ่งที่ระบบ CSP-X1 พยากรณ์กับสิ่งที่ผู้ใช้ทำจริง แล้วแปลงเป็นคะแนน **QoU (Quality of Unpredictability)** เพื่อใช้ทั้งในการให้รางวัลเชิงเศรษฐกิจ (เครดิต/โทเค็นภายในระบบ) และสร้างข้อมูลใหม่เพื่อลดความเสี่ยง **Model Collapse**.

## 2) ขอบเขต (Scope)

### In-Scope
- การคำนวณ QoU แบบ real-time.
- โครงสร้างข้อมูล Entropy Packet และ Ledger สำหรับข้อมูล high-entropy.
- อินเทอร์เฟซ API สำหรับรับ packet และคืนผลการประเมิน.
- Anti-gaming logic เพื่อแยก "noise" ออกจาก "novel creativity".

### Out-of-Scope
- การแลกโทเค็นกับเงินจริง (Fiat) ในเฟสแรก.
- การ train LLM ใหม่ทั้งโมเดล (เฟสนี้รองรับ fine-tune / RAG pipeline เท่านั้น).

## 3) องค์ประกอบระบบ (System Components)

### 3.1 CSP-X1 Prediction Engine (The Oracle)
- รัน shadow prediction เพื่อคาดการณ์ action ถัดไป.
- ส่ง confidence score เข้า entropy pipeline.

### 3.2 Entropy Validator (The Judge)
- เปรียบเทียบ `prediction_snapshot.confidence_score` กับ action จริง.
- คำนวณ QoU จากสูตรหลัก และกำหนด state ของ Singularity Meter.
- ทำ anti-gaming และ safety filter.

### 3.3 Akashic Treasury (The Ledger)
- บันทึกธุรกรรม QoU เป็น hash-chain.
- Packet ที่ QoU สูงถูกทำเครื่องหมาย preserve พร้อม artifact reference.

### 3.4 GunUI Feedback Layer (The Sensor)
- ใช้ข้อมูลการประเมินเพื่อแสดงสถานะ visual feedback:
  - Predictable → เทา/ขาว
  - Divergent → ส้ม/ม่วง
  - Chaotic/Genius → ทอง + particle explosion

## 4) Interface Contract

### 4.1 Entropy Submit API

`POST /api/v1/entropy/submit`

**Headers**
- `Content-Type: application/json`
- `Authorization: Bearer <user_token>` (policy-level contract)

**Body (ย่อ)**
```json
{
  "user_id": "uuid-v4",
  "packet": {
    "packet_id": "uuid-v4",
    "timestamp": "2023-10-27T10:00:00Z",
    "user_context": {
      "current_screen": "dashboard",
      "previous_actions": ["click_home", "scroll_down"]
    },
    "prediction_snapshot": {
      "model_version": "CSP-X1-Beta",
      "predicted_action": "click_notification",
      "confidence_score": 0.95
    },
    "actual_action": {
      "type": "creative_writing",
      "content_hash": "sha256_of_content",
      "input_method": "voice_dictation",
      "content_preview": "optional short text",
      "micro_metrics": {
        "typing_variance": 0.4,
        "hesitation_pauses": 2,
        "mouse_jitter": 0.3,
        "voice_tone_variance": 0.2
      }
    }
  }
}
```

## 5) Data Schema

### 5.1 Entropy Packet
- รองรับ context, prediction snapshot, actual action, micro-interaction metrics.
- รองรับ `content_preview` เพื่อ semantic/noise safety checks.

### 5.2 Ledger (Logical SQL Shape)
```sql
CREATE TABLE entropy_ledger (
    id UUID PRIMARY KEY,
    user_id UUID,
    qou_score DECIMAL(5,4),
    reward_amount INTEGER,
    artifact_ref TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 6) Algorithms

### 6.1 QoU Formula

\[
QoU = (1 - P_{model}(action|context)) \times W_{semantic} \times W_{safety}
\]

- `P_model`: confidence ของ model ต่อ action ที่เกิดขึ้น.
- `W_semantic`: น้ำหนักเชิงความหมาย (noise = 0).
- `W_safety`: safety guard (harmful = 0).

### 6.2 Rendering/Preserve Trigger
- เมื่อ `QoU > 0.8`:
  - Meter state = `chaotic_genius`
  - Trigger visual glitch / particle effect
  - set preserve flag
  - mark candidate for immediate model update pipeline

## 7) Policies

### 7.1 Pricing Policy
- Routine commodity actions: คิดค่าบริการตาม usage.
- Novel creative actions: reward ตามช่วง QoU.

### 7.2 Integrity Policy
- ข้อมูล raw imperfect มีมูลค่าสูงกว่าข้อมูลที่ผ่านการ self-healing.
- Original glitch artifact ต้อง trace ได้ใน ledger chain.

## 8) Safety & Governance

### 8.1 Chaos Filter
- Layer 1: ป้องกัน spam/repetition/noise.
- Layer 2: ป้องกัน harmful content (safety weight = 0).

### 8.2 Human-in-the-Loop Override
- สิทธิ์ระดับ Architect สามารถ review tuning ของ weight/policy ได้.

## 9) Test Plan

| Test Case | Description | Expected Outcome |
|---|---|---|
| TC-01 | User ทำ action ที่ predictable สูง | QoU < 0.1 และระบบคิดค่าบริการ |
| TC-02 | User ส่ง noise (keyboard smash) | semantic weight = 0, QoU = 0 |
| TC-03 | User ส่ง creative poem ที่คาดไม่ถึง | QoU > 0.8, ได้ reward, trigger visual glitch |
| TC-04 | Load test 10k packets concurrent | latency validator + bus < 50ms (target)
|

## 10) Implementation Mapping (Current Alpha)

- `src/backend/genesis_core/entropy/schemas.py`
  - นิยามสัญญา EntropyPacket / Assessment / Submit payload.
- `src/backend/genesis_core/entropy/service.py`
  - QoU calculation + anti-gaming + safety logic.
- `src/backend/genesis_core/entropy/ledger.py`
  - hash-chain style treasury ledger.
- `src/backend/routers/entropy.py`
  - endpoint `/api/v1/entropy/submit`.
- `src/backend/main.py`
  - wiring validator + treasury เข้าสู่ app state และเปิดใช้งาน router.

