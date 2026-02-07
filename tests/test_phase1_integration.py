import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
import json

def test_websocket_flow():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        # 1. Send INTENT_START
        websocket.send_text(json.dumps({"type": "INTENT_START"}))
        ack = websocket.receive_json()
        assert ack["type"] == "ACK"
        assert ack["for"] == "INTENT_START"

        # 2. Send INTENT_RECOGNIZED (Text Input)
        # "Make a blue sphere"
        websocket.send_text(json.dumps({
            "type": "INTENT_RECOGNIZED",
            "text": "Make a blue sphere"
        }))

        # 3. Expect VISUAL_PARAMS
        # Response might be chunked. The server sends VISUAL_PARAMS first, then AI_SPEAK.
        res1 = websocket.receive_json()
        print("Received:", res1)

        # Check if it's VISUAL_PARAMS
        if res1["type"] == "VISUAL_PARAMS":
            assert res1["params"]["base_shape"] == "sphere"
            # SimulatedInterpreter logic: "blue" -> #0000FF
            assert res1["params"]["color_palette"] == "#0000FF"
        else:
            # It might be AI_SPEAK if logic is fast? Unlikely order but possible.
            # Server code: await send_text(VISUAL); await send_text(AI_SPEAK)
            # So VISUAL should be first.
            pytest.fail(f"Expected VISUAL_PARAMS, got {res1['type']}")
