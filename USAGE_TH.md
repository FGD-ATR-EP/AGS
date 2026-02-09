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

## 2. API & การเชื่อมต่อ (Connectivity)
สำหรับนักพัฒนาที่ต้องการเชื่อมต่อกับ "Cognitive Core" ของระบบโดยตรง

*   **WebSocket Endpoint:** `ws://localhost:8000/ws` และ `ws://localhost:8000/ws/v3/stream`
    *   ใช้สำหรับส่งข้อความ (Intent) และรับข้อมูลสถานะ/ภาพแบบ Real-time
*   **Health Check Protocol:** ระบบจะกระจายสัญญาณความพร้อม (Heartbeat) ผ่าน AetherBus ซึ่งสามารถติดตามได้ผ่านการเชื่อมต่อ WebSocket เดียวกัน
