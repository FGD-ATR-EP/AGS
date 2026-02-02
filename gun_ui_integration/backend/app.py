import os
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import time
try:
    from .state_manager import StateManager
except ImportError:
    from state_manager import StateManager

app = FastAPI()

state_manager = StateManager()

# หา Path ของไฟล์ index.html โดยอ้างอิงจากตำแหน่งของไฟล์ app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend", "index.html")

@app.get("/")
async def get():
    with open(FRONTEND_PATH, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            start = time.perf_counter()
            # ส่ง State และ Color ไปยัง Frontend
            await websocket.send_json({
                "state": state_manager.state,
                "color": state_manager.color
            })

            # คำนวณ Latency (Round Trip Time simulation)
            latency = (time.perf_counter() - start) * 1000
            print(f"Update sent. Latency check: {latency:.2f} ms")

            await asyncio.sleep(0.05) # เพิ่มความถี่เป็น 20Hz (0.05s) เพื่อความลื่นไหล
    except Exception as e:
        print(f"Connection closed: {e}")
