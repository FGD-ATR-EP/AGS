import time
import webbrowser
import os
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class GunUI:
    def __init__(self):
        self.current_mode = "IDLE"
        self.interface_opened = False

    def launch_interface(self):
        """เปิดหน้าจอ Living Interface"""
        # ใช้ path แบบสัมพัทธ์เพื่อให้หาไฟล์เจอไม่ว่าจะอยู่ที่ไหน
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(current_dir, "gunui", "living_interface.html")
            
            if os.path.exists(path):
                print(f"{Fore.CYAN}[System]: Launching Neural Interface...")
                # เปิดไฟล์ html ใน browser (ถ้าทำได้)
                webbrowser.open(f"file://{path}")
                self.interface_opened = True
            else:
                print(f"{Fore.RED}[Error]: File not found: {path}")
        except Exception as e:
            print(f"{Fore.RED}[Error]: Could not launch interface. {e}")

    def morph_ui(self, shape_command):
        """สั่งเปลี่ยนรูปร่าง UI"""
        self.current_mode = shape_command
        print(f"\n{Fore.CYAN}>>> UI MORPHING >>> {shape_command}")
        
        if shape_command == "WAVE":
            print(f"{Fore.GREEN}   [Visual]: Particles aligning to Sound Frequency (Voice Mode)")
        elif shape_command == "DOC":
            print(f"{Fore.YELLOW}   [Visual]: Particles forming Document Structure")
        elif shape_command == "CIRCLE":
            print(f"{Fore.BLUE}   [Visual]: Particles forming Core Identity (Standby)")

    def visualize_voice(self, intensity):
        """จำลองกราฟเสียง"""
        bar = "||" * int(intensity)
        print(f"\r{Fore.GREEN}[Voice Input]: {bar}", end="")

    # --- ส่วนแสดงผลข้อความเดิม ---
    def show_nirodha_state(self):
        print(f"\n{Fore.BLACK}{Style.BRIGHT}[GunUI]: ⚫ SYSTEM STATE: NIRODHA (Deep Sleep)")
        print(f"{Fore.BLACK}   ...Particles are static... Waiting for signal...")

    def show_pre_cognition(self):
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}[GunUI]: 🟡 SYSTEM STATE: PRE-COGNITION")
        print(f"{Fore.YELLOW}   ...Particles spinning... Gate Detected.")

    def show_awakened(self):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}[GunUI]: 🔵 SYSTEM STATE: AWAKENED")
        print(f"{Fore.CYAN}   ...Particles Flowing Coherently... Shelvas is Online.")
        print(f"{Fore.GREEN}   >> Welcome back, Partner.")

    def show_access_denied(self):
        print(f"\n{Fore.RED}{Style.BRIGHT}[GunUI]: 🔴 ACCESS DENIED")
