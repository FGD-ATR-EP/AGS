# Resonance/Entropy Architecture → AI Partner Model Mapping

เอกสารนี้สรุปว่า architecture เดิมที่มีแกน **Resonance + Entropy** ยังถูกเก็บไว้ตรงไหนในโมเดล **AI Partner** ใหม่

## 1) Resonance layer (Intent alignment / interaction quality)

- เดิม: โฟกัสเรื่องการ “จูน” การสื่อสารและความสอดคล้องกับผู้ใช้
- ใหม่ (AI Partner):
  - `ValidatorAgent` ใช้เป็น alignment gate ก่อน action (`audit_gate`) เพื่อรักษาความสอดคล้องเชิงนโยบาย
  - `Reflector` สกัด Gem จาก episode เพื่อเรียนรู้รูปแบบการสื่อสาร/พฤติกรรมที่เหมาะสม แต่หยุดที่สถานะ PROPOSED
  - `PolicyUpdater` ทำหน้าที่ promote Gem ภายใต้ governance เท่านั้น (ไม่ auto-active จาก reflection)

## 2) Entropy layer (Risk / irreversible impact / uncertainty)

- เดิม: ระบบคิดเชิง entropy สำหรับผลกระทบและความไม่แน่นอน
- ใหม่ (AI Partner):
  - `GovernanceCore.assess_risk(...)` แปลง action เป็น Tier 0-3
  - Tier 2/3 ถูกผูกกับ approval workflow และบันทึกลง Akashic ledger
  - `simulate_rule_promotion(..., shadow_mode=True)` เพิ่ม policy simulator/shadow mode ก่อนเปิดใช้กฎจริง

## 3) Akashic + Derived memory (continuity/provenance)

- เดิม: บันทึกแบบ ledger สำหรับเหตุการณ์
- ใหม่ (AI Partner):
  - Akashic ledger ยังเป็น immutable chain เดิม
  - เพิ่ม derived store `data/derived_gems.json` สำหรับสถานะปัจจุบันของ Gem
  - ทุกการเปลี่ยนสถานะ Gem (approved/active/deprecated) ถูกเขียนทั้ง ledger + derived พร้อม provenance:
    - adopted_by
    - adopted_at
    - source_episode

## 4) Dashboard responsibilities (modular UI)

- เดิม: dashboard ไฟล์เดียว
- ใหม่:
  - `approvalInbox.js` รับผิดชอบ Approval Inbox
  - `actionPreview.js` รับผิดชอบ preview panel
  - `gemPanel.js` รับผิดชอบ gem panel
  - `main.js` ทำ orchestration + polling

## 5) Episode replay model for reflector

- เพิ่ม `ReplayableEpisode` เพื่อเก็บ episode ที่ replay ได้
- `reflect_on_episode(...)` เก็บ episode ลง history
- `replay_episode(...)` สร้าง reflection ใหม่จาก episode เดิม โดยใส่ metadata `replayed_from`

