import time
import webbrowser
import os
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

class GunUI:
    def __init__(self):
        self.current_mode = "IDLE"
        self.interface_opened = False

    # --- Section 1: Web Interface Control (Living UI) ---
    
    def launch_interface(self):
        """เปิดหน้าจอ Living Interface (HTML Canvas) ใน Browser"""
        # ตรวจสอบ path ให้ถูกต้องตามโครงสร้างไฟล์
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "gunui", "living_interface.html")
        
        if os.path.exists(path):
            print(f"{Fore.CYAN}[System]: Launching Neural Interface at {path}")
            webbrowser.open(f"file://{path}")
            self.interface_opened = True
        else:
            print(f"{Fore.RED}[Error]: Interface file not found at {path}")
            print(f"{Fore.YELLOW}[Hint]: Make sure 'living_interface.html' is inside 'gunui' folder.")

    def morph_ui(self, shape_command):
        """สั่งเปลี่ยนรูปร่าง UI (CIRCLE, WAVE, DOC)"""
        self.current_mode = shape_command
        # ในอนาคตบรรทัดนี้จะส่ง WebSocket message ไปยัง Browser
        print(f"\n{Fore.CYAN}>>> UI MORPHING >>> {shape_command}")
        
        if shape_command == "WAVE":
            print(f"{Fore.GREEN}   [Visual]: Particles aligning to Sound Frequency (Voice Mode)")
        elif shape_command == "DOC":
            print(f"{Fore.YELLOW}   [Visual]: Particles forming Document Structure")
        elif shape_command == "CIRCLE":
            print(f"{Fore.BLUE}   [Visual]: Particles forming Core Identity (Standby)")

    def visualize_voice(self, intensity):
        """จำลองการตอบสนองต่อเสียง"""
        bar = "||" * int(intensity)
        print(f"\r{Fore.GREEN}[Voice Input]: {bar}", end="")

    # --- Section 2: Terminal Visuals (CLI Status) ---

    def show_nirodha_state(self):
        print(f"\n{Fore.BLACK}{Style.BRIGHT}[GunUI]: ⚫ SYSTEM STATE: NIRODHA (Deep Sleep)")
        print(f"{Fore.BLACK}   ...Particles are static... Waiting for signal...")

    def show_pre_cognition(self):
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}[GunUI]: 🟡 SYSTEM STATE: PRE-COGNITION")
        print(f"{Fore.YELLOW}   ...Particles spinning (Vorticity Rising)... Gate Detected.")

    def show_awakened(self):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}[GunUI]: 🔵 SYSTEM STATE: AWAKENED")
        print(f"{Fore.CYAN}   ...Particles Flowing Coherently... Shelvas is Online.")
        print(f"{Fore.GREEN}   >> Welcome back, Partner.")

    def show_access_denied(self):
        print(f"\n{Fore.RED}{Style.BRIGHT}[GunUI]: 🔴 ACCESS DENIED")
        print(f"{Fore.RED}   ...Chaos Detected... Reverting to Sleep Mode.")

    def animate_boot_sequence(self):
        print(f"\n{Fore.MAGENTA}>>> LOADING KERNEL: INSPIRA MODULE <<<")
        loading_bar = ["|", "/", "-", "\\"]
        # Animation loop
        for _ in range(5):
            for char in loading_bar:
                print(f"\r{Fore.MAGENTA}Syncing Consciousness... {char}", end="")
                time.sleep(0.1)
        print(f"\r{Fore.MAGENTA}Syncing Consciousness... COMPLETE.   ")