from fastapi.testclient import TestClient
from src.backend.main import app
import json

client = TestClient(app)


def test_websocket_standard_spawn():
    with client.websocket_connect("/ws") as websocket:
        payload = {
            "mode": "std",
            "input": {
                "type": "touch",
                "region": [0.1, 0.1, 0.2, 0.2],
                "pressure": 0.5
            }
        }
        websocket.send_text(json.dumps(payload))
        data = websocket.receive_text()
        instruction = json.loads(data)

        assert instruction["intent"] == "SPAWN"
        assert instruction["shape"] == "organic"
        # Pydantic tuple vs list conversion
        assert list(instruction["region"]) == [0.1, 0.1, 0.2, 0.2]


def test_websocket_standard_voice_move():
    with client.websocket_connect("/ws") as websocket:
        payload = {
            "mode": "std",
            "input": {
                "type": "voice",
                "text": "move objects"
            }
        }
        websocket.send_text(json.dumps(payload))
        data = websocket.receive_text()
        instruction = json.loads(data)

        assert instruction["intent"] == "MOVE"
        # LCL defaults
        assert instruction["vector"] == [0.0, 0.0]


def test_websocket_ai_mock_move_right():
    with client.websocket_connect("/ws") as websocket:
        payload = {
            "mode": "ai",
            "input": {
                "text": "move the tree right"
            }
        }
        websocket.send_text(json.dumps(payload))
        data = websocket.receive_text()
        instruction = json.loads(data)

        assert instruction["intent"] == "MOVE"
        assert instruction["target"] == "TREE_CLUSTER_RIGHT"
        assert instruction["vector"] == [-0.25, 0.0]


def test_websocket_ai_mock_spawn():
    with client.websocket_connect("/ws") as websocket:
        payload = {
            "mode": "ai",
            "input": {
                "text": "spawn a star"
            }
        }
        websocket.send_text(json.dumps(payload))
        data = websocket.receive_text()
        instruction = json.loads(data)

        assert instruction["intent"] == "SPAWN"
        assert instruction["color_profile"] == "natural_green"
