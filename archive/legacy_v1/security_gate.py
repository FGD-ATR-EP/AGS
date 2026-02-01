import time
import getpass
import config
from visual_engine import GunUI

class AccessController:
    def __init__(self, device_type=config.DEFAULT_DEVICE):
        self.state = "NIRODHA"
        self.knock_count = 0
        self.last_knock_time = 0
        self.device_type = device_type
        self.ui = GunUI()

    def process_knock(self):
        """ฟังก์ชันจับจังหวะการเคาะ (The Ritual)"""
        current_time = time.time()
        
        # รีเซ็ตถ้าเคาะห่างกันเกินกำหนด
        if current_time - self.last_knock_time > config.KNOCK_TIMEOUT:
            self.knock_count = 0
            
        self.knock_count += 1
        self.last_knock_time = current_time
        
        print(f"* KNOCK DETECTED * ({self.knock_count}/{config.REQUIRED_KNOCKS})")
        
        if self.knock_count >= config.REQUIRED_KNOCKS:
            self._trigger_gate()

    def _trigger_gate(self):
        """เมื่อเคาะครบ 3 ครั้ง ให้เรียกหน้าต่างปลดล็อค"""
        self.state = "PRE_COGNITION"
        self.ui.show_pre_cognition()
        
        is_authenticated = False
        if self.device_type == "MOBILE":
            is_authenticated = self._mobile_unlock()
        else:
            is_authenticated = self._desktop_unlock()

        if is_authenticated:
            self.ui.animate_boot_sequence()
            self.state = "AWAKENED"
            self.ui.show_awakened()
        else:
            self.ui.show_access_denied()
            self.state = "NIRODHA"
            self.knock_count = 0

    def _desktop_unlock(self):
        print(f"\n💻 [Security Gate]: Desktop Interface")
        try:
            # ใช้ getpass เพื่อซ่อนรหัสผ่าน (ทำงานได้ดีใน Terminal จริง)
            password = getpass.getpass(">> Enter Genesis Passcode: ")
        except:
            # Fallback กรณีรันในบาง IDE ที่ไม่รองรับ getpass
            password = input(">> Enter Genesis Passcode: ")
            
        return password == config.DESKTOP_PASSWORD

    def _mobile_unlock(self):
        print(f"\n📱 [Security Gate]: Mobile Interface")
        print(f"   (Hint: Draw the pattern '{config.MOBILE_PATTERN}')")
        pattern = input(">> Simulate Pattern Input: ")
        return pattern.upper() == config.MOBILE_PATTERN