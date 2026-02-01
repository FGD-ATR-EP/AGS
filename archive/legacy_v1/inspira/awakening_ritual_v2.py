# gunui/awakening_ritual.py
# โค้ดสำหรับจำลอง The Awakening Ritual (3-Tap Ritual) และการตอบสนองด้วย System Vital Signs

import time
import random
import json

class SystemVitalSigns:
    def __init__(self):
        self.cpu_load = 0.0
        self.memory_usage = 0.0
        self.battery_level = 100.0
        self.system_mood = "Resting"  # สถานะอารมณ์ของระบบ: Resting, Active, Excited, Overloaded

    def update_vitals(self, state):
        # อัปเดตสถานะของระบบตามการเคาะ
        if state == "Listening":
            self.cpu_load = random.uniform(10.0, 30.0)
            self.memory_usage = random.uniform(20.0, 40.0)
            self.system_mood = "Active"
        elif state == "Analyzing":
            self.cpu_load = random.uniform(40.0, 70.0)
            self.memory_usage = random.uniform(50.0, 70.0)
            self.system_mood = "Excited"
        elif state == "Awake":
            self.cpu_load = random.uniform(70.0, 90.0)
            self.memory_usage = random.uniform(80.0, 95.0)
            self.system_mood = "Excited"
        else:
            self.cpu_load = random.uniform(0.0, 5.0)
            self.memory_usage = random.uniform(5.0, 15.0)
            self.system_mood = "Resting"

    def get_vitals(self):
        return {
            "cpu_load": self.cpu_load,
            "memory_usage": self.memory_usage,
            "battery_level": self.battery_level,
            "system_mood": self.system_mood
        }

class AwakeningRitual:
    def __init__(self):
        self.tap_count = 0
        self.last_tap_time = 0
        self.state = "Sleep"
        self.vital_signs = SystemVitalSigns()

    def tap(self):
        current_time = time.time()
        if current_time - self.last_tap_time < 1:  # กำหนดเวลาระหว่างการเคาะไม่เกิน 1 วินาที
            self.tap_count += 1
            self.last_tap_time = current_time

            if self.tap_count == 1:
                self.state = "Listening"
                self.vital_signs.update_vitals(self.state)
                print(f"ระบบ: พร้อมรับการเคาะครั้งที่ 2 | {json.dumps(self.vital_signs.get_vitals(), indent=2)}")
            elif self.tap_count == 2:
                self.state = "Analyzing"
                self.vital_signs.update_vitals(self.state)
                print(f"ระบบ: พร้อมรับการเคาะครั้งที่ 3 | {json.dumps(self.vital_signs.get_vitals(), indent=2)}")
            elif self.tap_count == 3:
                self.state = "Awake"
                self.vital_signs.update_vitals(self.state)
                print(f"ระบบ: ปลุกสำเร็จ! ระบบพร้อมใช้งาน | {json.dumps(self.vital_signs.get_vitals(), indent=2)}")
            else:
                self.reset()
        else:
            self.reset()

    def reset(self):
        self.tap_count = 0
        self.state = "Sleep"
        self.vital_signs.update_vitals(self.state)
        print(f"ระบบ: รีเซ็ตการเคาะ | {json.dumps(self.vital_signs.get_vitals(), indent=2)}")

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    ritual = AwakeningRitual()
    print("โปรดเคาะ 3 ครั้งภายใน 1 วินาทีเพื่อปลุกระบบ")
    while True:
        input("กด Enter เพื่อจำลองการเคาะ...")
        ritual.tap()