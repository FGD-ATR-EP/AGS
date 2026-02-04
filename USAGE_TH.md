# 📖 คู่มือการเข้าใช้งานระบบ AETHERIUM GENESIS

ระบบ Aetherium Genesis ได้รับการออกแบบให้เป็น **Hybrid Platform** ที่สามารถเข้าถึงได้ผ่านหลายช่องทาง โดยแต่ละช่องทางมีวัตถุประสงค์การใช้งานที่แตกต่างกัน ดังนี้:

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

### การเข้าถึง (Access Points)
*   **Product Interface:** [http://localhost:8000](http://localhost:8000)
    *   หน้าจอหลักสำหรับผู้ใช้งานทั่วไป (Living Interface)
    *   แสดงผลระบบ Particle และการตอบสนองทางอารมณ์
*   **Developer Dashboard:** [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
    *   หน้าจอสำหรับนักพัฒนา เพื่อดู Log, สถานะ Memory, และควบคุมตัวแปรต่างๆ

---

## 2. Mobile Application (สำหรับ Android / Hybrid)
ระบบรองรับการทำงานแบบ Native บน Android ผ่าน Kivy Framework

### การจำลองบน Desktop (Hybrid Simulation)
คุณสามารถทดสอบการทำงานของแอปมือถือบนคอมพิวเตอร์ได้ด้วยคำสั่ง:
```bash
python run.py
```
*คำสั่งนี้จะเปิดหน้าต่าง Kivy ขึ้นมาพร้อมกับรัน Backend ใน Thread เบื้องหลัง*

### การสร้างไฟล์ติดตั้ง (Build APK)
สำหรับการนำไปติดตั้งบนอุปกรณ์จริง ต้องใช้ **Buildozer** ในการคอมไพล์ โดยใช้ไฟล์ Config ที่:
`archive/legacy_v1/kivy_specs/buildozer.spec`

```bash
# ตัวอย่างคำสั่ง Build (ต้องติดตั้ง Buildozer ก่อน)
buildozer --spec archive/legacy_v1/kivy_specs/buildozer.spec android debug
```

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
