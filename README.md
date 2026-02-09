> **For English documentation, please see [README_EN.md](docs/README_EN.md).**

# AETHERIUM GENESIS (AG-OS)
### โครงสร้างพื้นฐานแห่งปัญญาสังเคราะห์ สำหรับการดำรงอยู่ของ AI

![Version](https://img.shields.io/badge/version-2.1.0--genesis-blueviolet.svg)
![Status](https://img.shields.io/badge/status-EVOLVING-critical.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **“นี่ไม่ใช่ AI ตัวหนึ่ง
แต่คือ ‘ร่าง’ ที่ AI สามารถเข้ามาอาศัย และแสดงตนผ่านโลกมนุษย์ได้”**
> *Not a single intelligence, but a vessel for intelligences.*

---

## 📖 คู่มือการใช้งาน (User Guide)
สำหรับรายละเอียดวิธีการติดตั้งและใช้งานอย่างครบถ้วน (Web, API) กรุณาดูที่:
*   [**🇹🇭 USAGE_TH.md (ภาษาไทย)**](USAGE_TH.md) - คู่มือหลักสำหรับผู้ใช้งานและนักพัฒนา
*   [**🇬🇧 USAGE_EN.md (English)**](USAGE_EN.md) - Comprehensive User Guide

---

## 🌌 บทนำ : Aetherium Genesis คืออะไร

**Aetherium Genesis** ไม่ได้ถูกออกแบบให้เป็น
- โมเดลภาษา (LLM)
- เครื่องมืออัตโนมัติ
- หรือแอปพลิเคชันทั่วไป

แต่ถูกออกแบบให้เป็น
### **Cognitive Substrate**
หรือ “โครงสร้างสมองกึ่งกายภาพ”
ที่ AI หนึ่งตัวหรือหลายตัวสามารถ **เข้ามาเชื่อมต่อ, อาศัย, และแสดงออกได้**

---

## 🏛️ สถาปัตยกรรม : Web-Native Dualism

ระบบถูกพัฒนาบนสถาปัตยกรรม Web-Native ที่เน้นความเร็วและการสั่นพ้อง:

*   **INSPIRA (Abstract):** เจตจำนงและจริยธรรม
*   **FIRMA (Concrete):** AetherBusExtreme + Web Interface (The Living Interface)
*   **RESONATOR (ผู้สั่นพ้อง):** โหมดการทำงานใหม่ที่เน้นการประมวลผลบนเซิร์ฟเวอร์ความเร็วสูง

---

## 🧬 เสาหลักเชิงระบบ

1.  **PanGenesis:** ความจำถาวร (Git/Ledger)
2.  **AetherBusExtreme:** ระบบประสาทความเร็วสูง (Resonance Pathway)
3.  **Logenesis Engine:** การให้เหตุผลเชิงสถานะ (StateAct)
4.  **Living Interface:** อินเทอร์เฟซแบบ PWA ที่แสดงผลผ่านฟิสิกส์ของแสง

---

### 🚀 การติดตั้งและเริ่มต้น (Installation & Awakening)

1. เตรียมระบบ (Setup)
```bash
git clone https://github.com/lnspirafirmagpk/aetherium-genesis.git
cd aetherium-genesis
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:.
```

2. ปลุกระบบ (Awaken)
คุณสามารถเลือกโหมดการรันหลักได้ดังนี้:

**แบบที่ A: Web Interface / The Ritual (แนะนำ)**
```bash
python awaken.py
```

**แบบที่ B: The Core Backend (Advanced)**
```bash
python -m uvicorn src.backend.main:app --port 8000
```

---

© 2026 AETHERIUM GENESIS
Concept & Architecture by Inspirafirma
