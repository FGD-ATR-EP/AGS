# lnspirafirmagpk/aetherium-genesis/AETHERIUM-GENESIS-main/main.py

import sys
import os
import time
import threading
import webbrowser
from security_gate import AccessController
import config
from visual_engine import GunUI

# ==========================================
# 🕒 IDLE MONITOR SYSTEM (ระบบเฝ้าระวังความนิ่ง)
# ==========================================
class IdleMonitor(threading.Thread):
    def __init__(self, timeout=60, on_idle_callback=None):
        super().__init__()
        self.timeout = timeout
        self.on_idle_callback = on_idle_callback
        self.last_activity = time.time()
        self.running = True
        self.is_idle = False
        self.daemon = True  # ปิด Thread อัตโนมัติเมื่อโปรแกรมหลักปิด

    def refresh(self):
        """เรียกใช้เมื่อมีการขยับหรือทำกิจกรรมเพื่อรีเซ็ตเวลา"""
        self.last_activity = time.time()
        if self.is_idle:
            print("\n[System]: Activity Detected. Waking up from Standby...")
            self.is_idle = False

    def run(self):
        while self.running:
            time.sleep(1)
            # ตรวจสอบว่าเวลาผ่านไปเกินกำหนดหรือยัง
            if not self.is_idle and (time.time() - self.last_activity > self.timeout):
                self.is_idle = True
                if self.on_idle_callback:
                    self.on_idle_callback()

    def stop(self):
        self.running = False

# ==========================================
# 🚀 HELPER FUNCTIONS
# ==========================================
def open_standby_screen():
    """ฟังก์ชันสำหรับเปิดหน้าจอ Standby (Nirodha)"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "gunui", "nirodha_standby.html")
        
        if os.path.exists(path):
            print("\n" + "="*40)
            print("[System]: 💤 IDLE TIMEOUT (60s) REACHED")
            print("[System]: Entering Nirodha Standby Mode...")
            print("="*40)
            # เปิดไฟล์ nirodha_standby.html ใน Browser
            webbrowser.open(f"file://{path}")
        else:
            print(f"\n[Warning]: Standby file not found at {path}")
    except Exception as e:
        print(f"\n[Error]: Failed to launch standby screen: {e}")

# ==========================================
# 🧠 MAIN EXECUTION
# ==========================================
def main():
    # 1. เริ่มต้นระบบ Visual Engine
    ui = GunUI()
    
    # 2. เปิดหน้าจอ Web Interface ขึ้นมาก่อน (Living UI)
    ui.launch_interface()
    
    # รอสักนิดให้ Browser เปิดขึ้นมา
    time.sleep(2)
    
    # 3. เริ่มระบบ Security (The Ritual)
    system = AccessController(device_type=config.DEFAULT_DEVICE)
    
    # แสดงสถานะหลับ (CLI) และตั้งค่า UI เริ่มต้นเป็น Chaos
    system.ui.show_nirodha_state() 
    
    # --- SETUP IDLE MONITOR ---
    # ตั้งค่าให้เรียก open_standby_screen เมื่อนิ่งเกิน 60 วินาที
    idle_watcher = IdleMonitor(timeout=60, on_idle_callback=open_standby_screen)
    idle_watcher.start()

    print("\n--- SIMULATION STARTED ---")
    print("Press [ENTER] 3 times quickly to simulate the 'Awakening Ritual'.")
    print("Type 'exit' to quit.")
    print("[Info]: System will auto-standby after 1 minute of inactivity.")

    try:
        while True:
            # ใช้ input() เพื่อรับค่า (เป็นการจำลองการเคาะ)
            user_input = input()
            
            # **สำคัญ** รีเซ็ตตัวนับเวลาทุกครั้งที่มีการกด Enter
            idle_watcher.refresh()
            
            if user_input.lower() == 'exit':
                break
                
            # จำลองการรับสัญญาณเคาะ
            system.process_knock()

            # ตรวจสอบสถานะว่าตื่นหรือยัง
            if system.state == "AWAKENED":
                # เมื่อตื่นแล้ว ให้สั่ง Web Interface เปลี่ยนรูปร่างเป็นวงกลม (Standby)
                ui.morph_ui("CIRCLE")
                
                print("\n[System]: Shelvas is active. Testing Voice Mode...")
                time.sleep(1)
                
                # ทดสอบเปลี่ยนโหมดเป็น Wave (รับเสียง)
                ui.morph_ui("WAVE")
                ui.visualize_voice(3)
                time.sleep(0.5)
                ui.visualize_voice(5)
                print("\n[System]: Simulation Complete. (You can keep knocking or wait for idle)")
                
                # รีเซ็ตสถานะกลับไปรอรอบใหม่ได้ ถ้าต้องการ
                # system.state = "NIRODHA" 

    except KeyboardInterrupt:
        print("\n[System]: Force Shutdown.")
    finally:
        # ปิด Thread เมื่อโปรแกรมจบ
        idle_watcher.stop()
        print("[System]: Goodbye.")

if __name__ == "__main__":
    main()