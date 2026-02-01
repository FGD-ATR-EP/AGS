import asyncio
import json
import logging
import os
import sys

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import math
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.logenesis import LogenesisResponse, IntentPacket
from src.backend.genesis_core.models.visual import TemporalPhase, IntentCategory, BaseShape
from src.backend.auth.routes import router as auth_router
from src.backend.departments.development.javana_core.reflex_kernel import JavanaKernel
from src.backend.departments.development.javana_core.responses import REFLEX_PARAMS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherServer")

app = FastAPI()
app.include_router(auth_router)

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

@app.websocket("/ws/v2/stream")
async def websocket_v2_endpoint(websocket: WebSocket):
    """WebSocket endpoint for V2 Streaming Protocol.

    Handles continuous audio streaming (mocked) and text input events.
    Manages session-based intent processing and visual updates.

    Args:
        websocket: The WebSocket connection instance.
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
    """Legacy WebSocket endpoint for the Living Interface PWA and Actuator UI.

    Handles `INTENT_*` lifecycle events, resets, and legacy `logenesis` mode inputs.
    Provides immediate visual feedback (temporal pulse) before processing completes.

    Args:
        websocket: The WebSocket connection instance.
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

# 3. Mount Root (The Living Interface)
# NOTE: We mount src/frontend as root, so index.html is served at /
app.mount("/", StaticFiles(directory="src/frontend", html=True), name="root")
