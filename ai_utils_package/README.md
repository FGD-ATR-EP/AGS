# AI Utils Package

แพ็กเกจ Python สำหรับช่วยเตรียมข้อมูล (Preprocessing) สำหรับงาน AI และ Machine Learning

## การติดตั้ง

```bash
pip install ai_utils
```

## การใช้งาน

```python
from ai_utils.text.preprocess import clean_text

text = "Hello, World!"
cleaned = clean_text(text)
print(cleaned)  # output: hello world
```

## ฟีเจอร์
- Text Cleaning (ลบอักขระพิเศษ, แปลงเป็นตัวพิมพ์เล็ก)
