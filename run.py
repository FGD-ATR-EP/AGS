import os
import threading
import sys
import asyncio

# --- Kivy Imports (The Body) ---
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

# --- Backend Imports (The Soul) ---
import uvicorn

# เพิ่ม Path เพื่อให้ Python หา src เจอ
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.append(src_path)

class GenesisServerThread(threading.Thread):
    """
    เธรดสำหรับรันสมองกล (FastAPI) แยกต่างหากจาก UI
    """
    def __init__(self):
        super().__init__()
        self.daemon = True

    def run(self):
        try:
            # Import ภายใน run เพื่อป้องกัน Circular Import หรือ Error หาก Dependencies ไม่ครบในบาง Environment
            from backend.main import app

            # บน Android ควรใช้ host='0.0.0.0'
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info",
                reload=False
            )
        except Exception as e:
            print(f"❌ KERNEL ERROR: {e}")

class GenesisUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="AETHERIUM GENESIS\nMobile Node Initialized", halign='center'))

class GenesisApp(App):
    def build(self):
        # ปลุกชีพจร (Start Backend)
        self.server_thread = GenesisServerThread()
        self.server_thread.start()
        return GenesisUI()

if __name__ == '__main__':
    GenesisApp().run()
