# 📖 คู่มือการเข้าใช้งานระบบ AETHERIUM GENESIS

ระบบ Aetherium Genesis ได้รับการออกแบบให้เป็น **Web-Native Platform** ที่สามารถเข้าถึงได้ผ่านหลายช่องทาง โดยแต่ละช่องทางมีวัตถุประสงค์การใช้งานที่แตกต่างกัน ดังนี้:

---

## 1. Web Interface (สำหรับ Desktop และ Development)
นี่คือช่องทางหลักสำหรับการพัฒนาและทดสอบระบบ โดยจะแสดงผลผ่าน Web Browser

### วิธีการเรียกใช้งาน (How to Run)
**วิธีที่ 1: ผ่าน Ritual Script (แนะนำ)**
สคริปต์นี้จะทำการตรวจสอบความพร้อมของระบบ (System Check), ล้างหน่วยความจำ (Memory Purge), และเริ่มระบบให้โดยอัตโนมัติ
```bash
python awaken.py
```

**วิธีที่ 2: เรียกใช้งาน Core Backend โดยตรง**
หากต้องการกำหนดค่า Port หรือ Reload option เอง
```bash
export PYTHONPATH=$PYTHONPATH:.
python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### จุดเชื่อมต่อระบบ (Access Points)
*   **Product Interface:** [http://localhost:8000](http://localhost:8000)
    *   หน้าจอหลักสำหรับผู้ใช้ทั่วไป (The Living Interface)
    *   แสดงผลระบบอนุภาค (Particle System) และการตอบสนองทางอารมณ์
*   **Developer Dashboard:** [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
    *   ศูนย์ควบคุมสำหรับนักพัฒนา เพื่อดู Logs, สถานะความจำ และปรับแต่งตัวแปรต่างๆ

---


## 3. API & Connectivity
สำหรับนักพัฒนาที่ต้องการเชื่อมต่อกับ "สมอง" (Cognitive Core) ของระบบโดยตรง

*   **WebSocket Endpoint:** `ws://localhost:8000/ws`
    *   ใช้สำหรับส่งข้อความ (Text) และรับสถานะ (State/Visuals) แบบ Real-time
*   **Health Check Protocol:** ระบบมีการส่งข้อมูลสุขภาพ (Heartbeat) ผ่าน AetherBus ซึ่งสามารถดักจับได้ผ่าน WebSocket เดียวกัน

---

## 4. Genesis Journal CLI (แอปพลิเคชัน Python สำหรับบันทึกเจตจำนง)
แอปพลิเคชัน CLI นี้ใช้สำหรับบันทึกโน้ต/เจตจำนงแบบเรียบง่ายลงในไฟล์ `src/backend/data/genesis_journal.json`

### การเพิ่มบันทึก (Add Entry)
```bash
python -m src.backend.apps.genesis_journal add --title "จุดประสงค์" --content "บันทึกเจตจำนงที่ต้องการเก็บรักษา"
```

### การแสดงรายการล่าสุด (List Entries)
```bash
python -m src.backend.apps.genesis_journal list --limit 5
```

### การล้างบันทึกทั้งหมด (Clear Entries)
```bash
python -m src.backend.apps.genesis_journal clear --yes
```

---

## 5. การใช้คีย์ AETHERIUM-GENESIS API

หากต้องการเชื่อมต่อบริการที่ต้องใช้โมเดลภายนอก คุณจำเป็นต้องมี **API Key** ก่อน โดยทั่วไปการจัดการคีย์จะทำผ่านหน้าจัดการคีย์ของ AETHERIUM-GENESIS AI Studio

### สิ่งที่พบได้ในหน้าจัดการคีย์
โดยปกติหน้าคีย์ API จะมีข้อมูลสำคัญ เช่น
* **Key** (ชื่อ/รหัสคีย์)
* **Project** (โครงการที่คีย์สังกัด)
* **Created on** (วันที่สร้าง)
* **Quota tier** (ระดับโควตาการใช้งาน)
* เครื่องมือ **จัดกลุ่ม**, **กรองตาม**, และมุมมอง **โครงการทั้งหมด**

### วิธีเชื่อมต่อ API Key กับระบบ
เมื่อสร้างคีย์แล้ว คุณสามารถใช้งานได้ 2 วิธีหลัก:

1. **ตั้งค่าเป็นตัวแปรสภาพแวดล้อม (แนะนำ)**
   ```bash
   export AETHERIUM_API_KEY="your_api_key_here"
   ```
   จากนั้นเปิดระบบตามปกติ เช่น
   ```bash
   python awaken.py
   ```

2. **ระบุคีย์แบบ explicit ในโค้ดหรือไฟล์ตั้งค่า**
   เหมาะสำหรับงานทดสอบเฉพาะจุด แต่ไม่แนะนำให้ hard-code คีย์ใน repository

> 🔒 คำแนะนำด้านความปลอดภัย: อย่า commit API Key ลง Git โดยตรง และควรใช้ไฟล์ `.env` หรือ Secret Manager ในสภาพแวดล้อม production
