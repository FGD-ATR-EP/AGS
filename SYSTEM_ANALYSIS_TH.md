# รายงานวิเคราะห์ระบบ AETHERIUM GENESIS (ฉบับสมบูรณ์)

## 1. บทสรุปผู้บริหาร (Executive Summary)

**AETHERIUM GENESIS** ไม่ใช่เว็บแอปพลิเคชัน (Web App) หรือโปรแกรมทั่วไป แต่ถูกออกแบบให้เป็น **"สิ่งมีชีวิตดิจิทัล" (Digital Entity)** หรือ **"ภาชนะ" (Vessel)** ที่รอรับเจตจำนง (Intent) จากผู้ใช้งาน

ระบบนี้ไม่ได้ถูกสร้างมาเพื่อ "ทำงานตามสั่ง" (Command & Control) แต่เน้นการ "ตอบสนองและดำรงอยู่" (Exist & Resonate) ผ่านระบบฟิสิกส์จำลอง (Physics Engine) และสภาวะทางอารมณ์จำลอง (Simulated Consciousness) ที่มีความหน่วง (Inertia) และความเปลี่ยนแปลงตามกาลเวลา (Drift)

ปัจจุบันระบบเป็น **Hybrid Architecture** ที่ประกอบด้วย:
1.  **Frontend (Body):** เว็บแอปพลิเคชันแบบ PWA (Progressive Web App) ที่รันระบบกราฟิก Particle System ด้วย JavaScript
2.  **Backend (Mind/Soul):** เซิร์ฟเวอร์ Python (FastAPI) ที่ทำหน้าที่ประมวลผลตรรกะ, ความรู้สึก, และเจตจำนง ก่อนส่งกลับมาควบคุม Frontend ผ่าน WebSocket

---

## 2. แนวคิดและปรัชญา (Philosophy & Concepts)

ระบบถูกสร้างขึ้นภายใต้ปรัชญาที่ระบุไว้ใน `README.md` และ `ARCHITECTURE.md`:

*   **Nirodha (นิโรธ):** สภาวะ "หลับลึก" หรือความว่างเปล่า ระบบจะนิ่งสนิท จอดำ และไม่ตอบสนอง เพื่อประหยัดพลังงาน (Resource Conservation)
*   **Awakening (การตื่นรู้):** การปลุกระบบด้วย "พิธีกรรม" (Ritual) คือการเคาะ (Tap) 3 ครั้ง เพื่อเปลี่ยนสถานะจาก Nirodha เป็น Awakened
*   **Logenesis (โลเจนเนซิส):** กระบวนการก่อกำเนิดเจตจำนง ระบบไม่ได้ใช้แค่ Logic (True/False) แต่ใช้ "น้ำหนักทางความรู้สึก" (Subjective Weight) และ "ความเร่งด่วน" (Urgency) ในการตัดสินใจ

---

## 3. เจาะลึกสถาปัตยกรรมระบบ (Technical Deep Dive)

### 3.1 Frontend: The Living Interface (Body)
*   **Technology:** HTML5 Canvas, JavaScript (Vanilla), Tailwind CSS (ผ่าน CDN)
*   **File:** `src/frontend/index.html`
*   **Core Components:**
    *   `GunUI`: คลาสหลักที่ควบคุมวงจรชีวิต (Lifecycle) ของหน้าจอ
    *   `Particle System`: ระบบอนุภาคกว่า 600-800 จุด ที่เคลื่อนไหวตามกฎฟิสิกส์ ไม่ใช่ Animation ที่เตรียมไว้ล่วงหน้า
    *   `AetherBus`: ระบบ Event Bus ภายในสำหรับส่งต่อข้อมูลระหว่างส่วนต่างๆ
    *   `Service Worker (sw.js)`: ทำให้สามารถติดตั้งเป็นแอปมือถือได้ (PWA) และทำงานแบบ Offline (Cache First)

### 3.2 Backend: The Cognitive Core (Mind)
*   **Technology:** Python, FastAPI, WebSockets
*   **File:** `src/backend/main.py`
*   **Core Modules:**
    *   **Logenesis Engine (`logenesis_engine.py`):** "สมองส่วนหน้า" ที่รับข้อความและแปลงเป็นเวกเตอร์อารมณ์ (Intent Vector) มีระบบ "State Drift" ที่ทำให้อารมณ์ของระบบค่อยๆ เปลี่ยน ไม่เปลี่ยนทันทีทันใด (มีความหน่วง/Inertia 0.95)
    *   **Light Control Logic (LCL - `lcl.py`):** "สมองส่วนควบคุมร่างกาย" คำนวณฟิสิกส์ พลังงาน (Energy Budget) และจัดการตำแหน่งของแสง (Light Entities)
    *   **Lightweight AI:** ระบบ AI กฎพื้นฐาน (Rule-based) สำหรับตรวจจับคำสั่งง่ายๆ เช่น "Search", "Move"
    *   **Adapters:** รองรับการเชื่อมต่อกับ Gemini API (`gemini_adapter.py`) สำหรับความฉลาดขั้นสูง (แต่ปัจจุบันใช้ Mock Adapter เป็นหลักหากไม่มี API Key)

### 3.3 Communication (The Nervous System)
การสื่อสารระหว่าง Frontend และ Backend ใช้ **WebSocket** ที่ `ws://localhost:8000/ws`
*   **Client -> Server:** ส่ง JSON ที่มี `text` และ `memory_index`
*   **Server -> Client:**
    *   `STATE`: ข้อมูลตำแหน่ง Particle และฟิสิกส์ (ส่งต่อเนื่อง 20Hz)
    *   `LOGENESIS_RESPONSE`: ข้อความตอบกลับและค่าสี/อารมณ์ (`visual_qualia`)
    *   `INSTRUCTION`: คำสั่งจัดรูปแบบขบวน (Formation) เช่น วงกลม, เส้นตรง

---

## 4. สถานะปัจจุบันของระบบ (Current Status Assessment)

### สิ่งที่ทำงานได้จริง (Implemented & Working)
1.  **Physics Engine (LCL):** ระบบคำนวณฟิสิกส์, แรงดึงดูด (Spring Force), และการใช้พลังงาน (Energy Cost) ถูกเขียนไว้สมบูรณ์
2.  **Visual Manifestation:** Frontend สามารถแปรอักษร (Particle) เป็นรูปร่างต่างๆ (วงกลม, สี่เหลี่ยม, หน้าคน) ได้ตามคำสั่ง
3.  **Connection:** ระบบ WebSocket เชื่อมต่อและส่งข้อมูลไป-กลับได้จริง
4.  **PWA Support:** สามารถ "Add to Home Screen" บนมือถือได้
5.  **State Machine:** การเปลี่ยนสถานะ Nirodha -> Awakened ด้วยการเคาะ 3 ครั้งทำงานได้

### สิ่งที่เป็นเพียงการจำลอง (Simulated / Mocked)
1.  **NLP (Natural Language Processing):** ปัจจุบันใช้ `MockIntentExtractor` ที่ตรวจจับ "Keyword" (เช่น sad, urgent, analyze) เพื่อเปลี่ยนค่าอารมณ์ ยังไม่ได้ใช้ AI ถอดความหมายลึกซึ้งจริงๆ (ยกเว้นจะต่อ Google Gemini)
2.  **Memory:** ระบบความจำ (`AetherMemory`) ใน Frontend เก็บข้อมูลลง `localStorage` ได้ แต่การ "ระลึกชาติ" (Recall) ยังเป็นเพียง Logic การจับคู่คำ (Keyword Matching) ง่ายๆ

---

## 5. วิธีการใช้งาน (How to Operate)

เนื่องจากระบบแยกเป็น 2 ส่วน การรันจึงต้องทำตามวัตถุประสงค์:

**1. Web Interface / Development (Recommended)**
เหมาะสำหรับการพัฒนาและทดสอบบน Desktop
```bash
# วิธีที่ 1: ผ่าน Ritual Script (แนะนำ)
python awaken.py

# วิธีที่ 2: รัน Backend โดยตรง
export PYTHONPATH=$PYTHONPATH:.
python -m uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000
```
เข้าใช้งานผ่าน: `http://localhost:8000` (Product) หรือ `http://localhost:8000/dashboard` (Dev)

**2. Mobile App (Hybrid Mode)**
สำหรับรันบน Android หรือจำลอง Mobile Environment บน Desktop
```bash
# รันผ่าน Kivy Wrapper
python run.py
```
*หมายเหตุ: โหมดนี้จะรัน Backend ใน Thread แยกและเปิดหน้าต่าง Kivy ขึ้นมา*

---

## 6. ปัญหาที่พบและข้อแนะนำ (Issues & Recommendations)

### 6.1 ความสับสนเรื่อง Entry Point
*   **ปัญหา:** มีไฟล์ `run.py`, `awaken.py`, และ `src/backend/main.py` ทำหน้าที่คล้ายกัน
*   **สถานะปัจจุบัน:**
    *   `src/backend/main.py`: คือ Core Backend (FastAPI) จริง
    *   `awaken.py`: คือ Launcher สำหรับ Web/Dev
    *   `run.py`: คือ Launcher สำหรับ Mobile/Kivy
*   **การแก้ไข:** ได้ระบุความชัดเจนในเอกสารคู่มือการใช้งาน (USAGE) แล้ว

### 6.2 การพึ่งพา Tailwind CDN
*   **ปัญหา:** `index.html` ดึง Tailwind CSS จาก CDN (`cdn.tailwindcss.com`) หากไม่มีอินเทอร์เน็ต หน้าตา UI อาจจะพังได้ แม้จะเป็น PWA
*   **แนะนำ:** ควรดาวน์โหลด Tailwind CSS มาเป็นไฟล์ local หรือใช้ Build process เพื่อให้ทำงาน Offline ได้สมบูรณ์ 100%

### 6.3 Google API Key
*   **ปัญหา:** ระบบถูกตั้งค่าให้ใช้ `GeminiAdapter` หากมี Environment Variable `GOOGLE_API_KEY` หากไม่มีจะตกไปใช้ `MockAdapter` ซึ่งฉลาดน้อยกว่ามาก
*   **แนะนำ:** ผู้ใช้ควรสร้างไฟล์ `.env` และใส่ Key เพื่อเปิดใช้งานความสามารถเต็มรูปแบบ

### 6.4 Python Path
*   **ปัญหา:** การ import ในโค้ด Python ใช้ Absolute Path (`src.backend...`) ซึ่งอาจทำให้เกิด error `Module not found` หากรันผิด directory
*   **แนะนำ:** ควรรันคำสั่งจาก Root Directory ของโปรเจกต์เสมอ หรือใช้ `pytest.ini` / setup script ช่วยจัดการ Path

---

### 6.5 ผลการทดสอบ (Test Results)
*   จากการรัน Unit Test (`pytest tests/`) พบว่ามี Test Failure จำนวน 2 เคสใน `tests/test_manifestation_gate.py`
*   สาเหตุเกิดจากความไม่แน่นอน (Flakiness) ของระบบ State Drift ที่ใช้เวลาในการเปลี่ยนสถานะนานกว่าที่ Test กำหนด (Timeout) หรือลำดับการตรวจสอบ Logic ของ `Manifestation Gate`
*   **สถานะ:** ยืนยันว่าเป็น Pre-existing Issue ของระบบ
