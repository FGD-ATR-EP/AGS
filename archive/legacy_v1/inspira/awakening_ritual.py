# inspira/awakening_ritual.py
# โค้ดสำหรับจำลอง The Awakening Ritual (3-Tap Ritual)

import time

class AwakeningRitual:
    def __init__(self):
        self.tap_count = 0
        self.last_tap_time = 0
        self.state = "Sleep"

    def tap(self):
        current_time = time.time()
        if current_time - self.last_tap_time < 1:  # กำหนดเวลาระหว่างการเคาะไม่เกิน 1 วินาที
            self.tap_count += 1
            self.last_tap_time = current_time

            if self.tap_count == 1:
                self.state = "Listening"
                print("ระบบ: พร้อมรับการเคาะครั้งที่ 2")
            elif self.tap_count == 2:
                self.state = "Analyzing"
                print("ระบบ: พร้อมรับการเคาะครั้งที่ 3")
            elif self.tap_count == 3:
                self.state = "Awake"
                print("ระบบ: ปลุกสำเร็จ! ระบบพร้อมใช้งาน")
            else:
                self.reset()
        else:
            self.reset()

    def reset(self):
        self.tap_count = 0
        self.state = "Sleep"
        print("ระบบ: รีเซ็ตการเคาะ")

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    ritual = AwakeningRitual()
    print("โปรดเคาะ 3 ครั้งภายใน 1 วินาทีเพื่อปลุกระบบ")
    while True:
        input("กด Enter เพื่อจำลองการเคาะ...")
        ritual.tap()