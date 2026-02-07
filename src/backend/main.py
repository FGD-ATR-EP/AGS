import asyncio
import json
import logging
import os
import sys
import time
import msgpack

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to load uvloop for high performance (Server Mode)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

import math
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.logenesis import LogenesisResponse, IntentPacket
from src.backend.genesis_core.models.visual import TemporalPhase, IntentCategory, BaseShape
from src.backend.auth.routes import router as auth_router
# Aetherium API Imports
from src.backend.routers.aetherium import router as aetherium_router
from src.backend.routers.metrics import router as metrics_router
from src.backend.routers.metrics import MetricCollector
from src.backend.routers.entropy import router as entropy_router
from src.backend.genesis_core.bus.extreme import AetherBusExtreme
from src.backend.security.key_manager import KeyManager
from src.backend.genesis_core.entropy import AkashicTreasury, EntropyValidator

from src.backend.departments.development.javana_core.reflex_kernel import JavanaKernel
from src.backend.departments.development.javana_core.responses import REFLEX_PARAMS

# Auditorium Imports
from src.backend.genesis_core.auditorium.service import AuditoriumService
from src.backend.genesis_core.bus.factory import BusFactory
import zlib
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherServer")

# --- Gatekeeper Middleware (Rate Limiting) ---
class GatekeeperMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {} # IP -> (timestamp, count)
        # Simple token bucket or window
        self.RATE_LIMIT = 1000 # requests per second (Very high for internal, adjust for public)

    async def dispatch(self, request: Request, call_next):
        # Basic Logic:
        # In a real scenario, use Redis. Here strictly in-memory for demo/speed.
        client_ip = request.client.host
        now = time.time()

        # Cleanup old entries (lazy)
        if client_ip in self.request_counts:
            ts, count = self.request_counts[client_ip]
            if now - ts > 1.0:
                 self.request_counts[client_ip] = (now, 1)
            else:
                 if count > self.RATE_LIMIT:
                     # 429 Too Many Requests
                     return JSONResponse(status_code=429, content={"error": "Gatekeeper: Rate Limit Exceeded"})
                 self.request_counts[client_ip] = (ts, count + 1)
        else:
             self.request_counts[client_ip] = (now, 1)

        response = await call_next(request)
        return response

app = FastAPI()
app.add_middleware(GatekeeperMiddleware)
app.include_router(auth_router)
app.include_router(aetherium_router)
app.include_router(metrics_router)
app.include_router(entropy_router)

# Global Services
auditorium: Optional[AuditoriumService] = None

# --- DEEPGRAM INTERFACE STUB ---
class DeepgramTranscriber:
    """Interface for Deepgram Live Transcription.

    Disabled by default, using Mock Mode in development.
    """
    def __init__(self, api_key: str = None):
        """Initializes the transcriber.

        Args:
            api_key: The Deepgram API key. If None, the transcriber is disabled.
        """
        self.api_key = api_key
        self.enabled = False # Set to True if API key is provided and needed

    async def transcribe_stream(self, audio_chunk: bytes):
        """Transcribes a chunk of audio data.

        Args:
            audio_chunk: Raw audio bytes.

        Returns:
            The transcribed text, or None if disabled.
        """
        if not self.enabled:
            return None
        # Actual Deepgram implementation would go here
        return "Deepgram Transcription Placeholder"

# Initialize Engine and Transcriber
engine = LogenesisEngine()
transcriber = DeepgramTranscriber(api_key=os.getenv("DEEPGRAM_API_KEY"))
# Initialize JAVANA (The Reflex System)
javana = JavanaKernel()

clients = set()

@app.on_event("startup")
async def startup_event():
    global auditorium

    # Awakening: Start the Bio-Digital Organism
    await engine.startup()

    # Initialize AetherBusExtreme (V2 Protocol)
    # We attach it to app.state for the API Router to use
    aether_bus = AetherBusExtreme()
    await aether_bus.connect()
    app.state.aether_bus = aether_bus
    app.state.engine = engine # Expose engine to router

    # Initialize Security & Metrics
    app.state.key_manager = KeyManager()
    app.state.entropy_validator = EntropyValidator()
    app.state.akashic_treasury = AkashicTreasury()

    metric_collector = MetricCollector.get_instance()
    app.state.metric_collector = metric_collector

    # Hook Metrics to Bus
    await aether_bus.add_global_listener(metric_collector.track_event)

    # Start Metrics Broadcast Loop
    asyncio.create_task(metric_collector.broadcast_loop())

    # Start Auditorium Service
    auditorium = AuditoriumService(engine)
    auditorium.start()

    # Start Health Broadcast Bridge
    asyncio.create_task(health_broadcast_loop())

@app.on_event("shutdown")
async def shutdown_event():
    # Enter Nirodha
    await engine.shutdown()

    if hasattr(app.state, "aether_bus"):
        await app.state.aether_bus.close()

    if auditorium:
        await auditorium.stop()

async def broadcast_to_clients(message: dict):
    if not clients:
        return
    txt = json.dumps(message)
    disconnected = set()
    for ws in clients:
        try:
            await ws.send_text(txt)
        except Exception:
            disconnected.add(ws)
    for ws in disconnected:
        clients.discard(ws)

async def health_broadcast_loop():
    """Reads health reports from AetherBus and broadcasts to WebSockets."""
    bus = BusFactory.get_bus()

    # Ensure connected
    try:
        await bus.connect()
    except Exception as e:
        logger.warning(f"Health Broadcast: Connect Warning: {e}")

    logger.info("Health Broadcast Loop Started")

    async def on_health_report(envelope):
        try:
            data = None
            try:
                # Try unpack msgpack (AetherBusExtreme)
                data = envelope.unpack_payload()
            except Exception:
                # Fallback to JSON (HyperSonic Legacy)
                try:
                    data = json.loads(envelope.payload)
                except Exception:
                    pass

            if data:
                msg = {
                    "type": "HEALTH_UPDATE",
                    "payload": data
                }
                await broadcast_to_clients(msg)
        except Exception as e:
            logger.error(f"Health Broadcast Handler Error: {e}")

    # Subscribe
    try:
        await bus.subscribe("system.health.report", on_health_report)
    except Exception as e:
        logger.error(f"Health Broadcast Subscribe Error: {e}")

    # Keep alive loop
    while True:
        await asyncio.sleep(3600)

@app.websocket("/ws/v2/stream")
async def websocket_v2_endpoint(websocket: WebSocket):
    """
    [DEPRECATED] WebSocket endpoint for V2 Streaming Protocol.
    Please migrate to /v1/session + /ws/v3/stream (Aetherium Protocol).
    """
    await websocket.accept()
    logger.info("V2 Client connected")
    session_id = str(id(websocket))

    try:
        while True:
            message = await websocket.receive()

            if "bytes" in message:
                # Handle binary audio (Mock: ignore or simple energy check)
                audio_data = message["bytes"]

                # --- JAVANA: Raw Speed Transducer ---
                # Calculate Energy (RMS) from raw bytes
                if len(audio_data) > 0:
                    # Simple RMS approximation (assuming 8-bit unsigned or just signal magnitude)
                    # Normalizing 0-255 byte values to 0.0-1.0 energy
                    # Using variance from 128 (silence) for better accuracy if 8-bit PCM
                    rms = math.sqrt(sum((b - 128)**2 for b in audio_data) / len(audio_data)) / 128.0

                    # Update JAVANA Sensory Memory
                    javana.update_sensors(energy=rms)

                    # Check for Reflex
                    reflex_action = javana.fast_react()
                    if reflex_action:
                        # INTERRUPT! Send Pre-baked Response immediately
                        p = REFLEX_PARAMS[reflex_action]
                        payload = {
                            "type": "VISUAL_UPDATE",
                            "payload": {
                                "intent": p["intent_category"],
                                "energy": p["energy_level"],
                                "shape": p["visual_parameters"]["base_shape"],
                                "color_code": p["visual_parameters"]["color_palette"]
                            },
                            "transcript_preview": f"[{reflex_action}]",
                            "text_content": None
                        }
                        await websocket.send_text(json.dumps(payload))
                        # continue # Skip AI processing for this frame (Optional, depending on desired overlap)
                        # We continue to let transcriber run, but visual feedback is hijacked.

                # In a real scenario, we'd feed this to transcriber
                continue

            elif "text" in message:
                try:
                    data = json.loads(message["text"])
                except json.JSONDecodeError:
                    continue

                # Mock Transcriber Logic: Receive text to simulate voice
                if data.get("type") in ["MOCK_TRANSCRIPTION", "TEXT_INPUT"]:
                    text = data.get("text", "")
                    logger.info(f"V2 Input: {text}")

                    packet = IntentPacket(
                        modality="text",
                        embedding=None,
                        energy_level=0.5,
                        confidence=1.0,
                        raw_payload=text
                    )
                    response: LogenesisResponse = await engine.process(packet, session_id=session_id)

                    if response.visual_analysis:
                        va = response.visual_analysis
                        payload = {
                            "type": "VISUAL_UPDATE",
                            "payload": {
                                "intent": va.intent_category,
                                "energy": va.energy_level,
                                "shape": va.visual_parameters.base_shape,
                                "color_code": va.visual_parameters.color_palette
                            },
                            "transcript_preview": text,
                            "text_content": response.text_content
                        }
                        await websocket.send_text(json.dumps(payload))

                elif data.get("type") == "GET_IDLE_STATE":
                    # Send initial idle parameters
                    payload = {
                        "type": "VISUAL_UPDATE",
                        "payload": {
                            "intent": "chat",
                            "energy": 0.1,
                            "shape": "sphere",
                            "color_code": "#06b6d4"
                        }
                    }
                    await websocket.send_text(json.dumps(payload))

    except WebSocketDisconnect:
        logger.info("V2 Client disconnected")
    except Exception as e:
        logger.error(f"V2 Server Error: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    [DEPRECATED] Legacy WebSocket endpoint.
    Maintained for Actuator UI and Living Interface PWA compatibility.
    """
    await websocket.accept()
    clients.add(websocket)
    logger.info("Client connected")

    # Session ID for state persistence (simple IP-based or random)
    session_id = str(id(websocket))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received")
                continue

            msg_type = msg.get("type")

            if msg_type == "PING":
                await websocket.send_text(json.dumps({"type": "PONG"}))
                continue

            # --- New Protocol (Actuator UI) ---
            if msg_type in ["INTENT_START", "INTENT_END", "INTENT_RECOGNIZED", "RESET"]:

                if msg_type == "INTENT_START":
                    await websocket.send_text(json.dumps({"type": "ACK", "for": "INTENT_START"}))

                elif msg_type == "INTENT_RECOGNIZED":
                    # Text from Client STT
                    text = msg.get("text", "")
                    logger.info(f"Processing Text: {text}")

                    # --- NEW: Immediate Temporal Pulse (Thinking) ---
                    # Send visual feedback BEFORE processing starts to eliminate stutter
                    thinking_params = engine.adapter.get_temporal_visuals(TemporalPhase.THINKING)
                    vp_thinking = thinking_params.model_dump(mode='json')

                    await websocket.send_text(json.dumps({
                        "type": "VISUAL_PARAMS",
                        "params": vp_thinking["visual_parameters"],
                        "meta": {
                            "category": vp_thinking["intent_category"],
                            "valence": vp_thinking["emotional_valence"],
                            "energy": vp_thinking["energy_level"]
                        }
                    }))
                    # -----------------------------------------------

                    packet = IntentPacket(
                        modality="text",
                        embedding=None,
                        energy_level=0.5,
                        confidence=1.0,
                        raw_payload=text
                    )
                    response: LogenesisResponse = await engine.process(packet, session_id=session_id)

                    # Convert LogenesisResponse to Client Protocol
                    # 1. Visual Params (Check Manifestation Gate)
                    if response.visual_analysis and response.manifestation_granted:
                        # Serialize Pydantic model
                        vp = response.visual_analysis.model_dump(mode='json')
                        # Flat map for the simple UI (or send full object)
                        # The UI expects 'VISUAL_PARAMS' with specific fields.
                        # I'll send the full structure and let UI parse it.
                        await websocket.send_text(json.dumps({
                            "type": "VISUAL_PARAMS",
                            "params": vp["visual_parameters"], # Send the specifics
                            "meta": {
                                "category": vp["intent_category"],
                                "valence": vp["emotional_valence"],
                                "energy": vp["energy_level"]
                            }
                        }))
                    elif response.visual_analysis and not response.manifestation_granted:
                         logger.info("Manifestation Gate: Blocked visual update (Conversational Loop)")

                    # 2. AI Speak
                    if response.text_content:
                        await websocket.send_text(json.dumps({
                            "type": "AI_SPEAK",
                            "text": response.text_content
                        }))

                elif msg_type == "RESET":
                    # Reset Engine State?
                    await websocket.send_text(json.dumps({"type": "ACK", "for": "RESET"}))

            # --- Legacy Protocol (Living Interface PWA) ---
            elif msg.get("mode") == "logenesis":
                # { mode: "logenesis", input: { text: "..." } }
                inp = msg.get("input", {})
                text = inp.get("text", "")

                packet = IntentPacket(
                    modality="text",
                    embedding=None,
                    energy_level=0.5,
                    confidence=1.0,
                    raw_payload=text
                )
                response: LogenesisResponse = await engine.process(packet, session_id=session_id)

                # Send back raw LogenesisResponse (PWA knows how to handle it)
                await websocket.send_text(response.model_dump_json())

    except WebSocketDisconnect:
        clients.discard(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"Server Error: {e}")

# Mount static files and routes (Must be after specific routes)

# 1. Specific Asset Routes (for clean URLs in PWA)
@app.get("/sw.js")
async def get_sw():
    return FileResponse("src/frontend/public/sw.js", media_type="application/javascript")

@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("src/frontend/public/manifest.json", media_type="application/json")

# 2. Mount Subdirectories
app.mount("/gunui", StaticFiles(directory="src/frontend/public/gunui"), name="gunui")
app.mount("/icons", StaticFiles(directory="src/frontend/public/icons"), name="icons")
app.mount("/public", StaticFiles(directory="src/frontend/public"), name="public")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("src/frontend/dashboard.html")

@app.get("/public")
async def public_gateway():
    return FileResponse("src/frontend/aether_public.html")

@app.get("/overseer")
async def overseer_gateway():
    return FileResponse("src/frontend/aether_overseer.html")

# 3. Mount Root (The Living Interface)
# NOTE: We mount src/frontend as root, so index.html is served at /
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="root")
