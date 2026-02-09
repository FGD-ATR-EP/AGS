from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.security.key_manager import KeyTier
import json
import time

def test_aetherium_flow():
    # Trigger Startup Events
    with TestClient(app) as client:
        # Inject an internal key for testing
        km = app.state.key_manager
        abe_id = "test-abe-id"
        test_key = km.create_key(abe_id=abe_id, tier=KeyTier.INTERNAL, label="Test Key")

        contract_data = {
            "identity": {
                "abe_id": abe_id,
                "entity_name": "Test Client"
            },
            "intent": {
                "primary_intent": "OBSERVER"
            }
        }

        # 1. Control Plane
        response = client.post("/v1/session", json={
            "client": "test_script",
            "access_key": test_key,
            "abe_contract": contract_data
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        session_id = data["session_id"]

        print(f"Session: {session_id}")

        # 2. Data Plane
        with client.websocket_connect(f"/ws/v3/stream?session_id={session_id}") as websocket:
            # Expect Handshake
            msg = websocket.receive_json()
            assert msg["type"] == "handshake"
            print("Handshake received")

            # Send Intent
            websocket.send_json({"text": "Hello Aether"})

            # Expect Stream
            received_types = []

            for _ in range(10): # Increased safety limit
                try:
                    msg = websocket.receive_json()
                    received_types.append(msg["type"])
                    print(f"Received: {msg['type']}")

                    if msg["type"] == "manifestation":
                        break
                    if msg["type"] == "degradation":
                        break
                except Exception as e:
                    print(f"Receive Error: {e}")
                    break

            assert "intent_detected" in received_types
            assert "state_update" in received_types
