# SYSTEM INTENT

## 1. Core Purpose
ระบบนี้ถูกออกแบบมาเพื่อรองรับการสร้างผลลัพธ์เชิงสร้างสรรค์
โดยมี “มนุษย์เป็นผู้กำหนดโครงสร้าง” และ AI เป็นผู้ดำเนินการสร้างตามเจตนา
ผ่าน correction events ที่มีขอบเขตชัดเจน

## 2. Primary Design Philosophy
- Human-guided > fully autonomous generation
- Local correctness > global optimization
- Explicit structure > implicit behavior

## 3. Non-Goals
ระบบนี้ *ไม่ถูกออกแบบมาเพื่อ*:
- เป็น conversational AI แบบทั่วไป
- รองรับ mobile-first หรือ low-end devices
- ทำ continual learning จากผู้ใช้โดยอัตโนมัติ
- Optimize เพื่อ cost-per-token ต่ำที่สุด

## 4. System Invariants (Must Not Change)
- Correction events เป็น first-class entity
- ทุก correction ต้องมี spatial/structural scope ชัดเจน
- ผลลัพธ์ต้อง deterministic ภายใน correction batch
- Core logic ต้องแยกจาก personalization และ scaling layer

## 5. Acceptable Trade-offs
- ยอม latency เพิ่ม เพื่อความถูกต้องของโครงสร้าง
- ยอม cost สูงใน early phase เพื่อ system clarity
- ยอม throughput ต่ำ เพื่อรักษา controllability
