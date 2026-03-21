from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.security.key_manager import KeyTier
from src.backend.routers.aetherium import _manifestation_bridge_payload
from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType
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
            assert msg["directive_state"]["correlation_id"] == session_id
            assert msg["directive_state"]["trace_id"] == session_id
            assert msg["directive_state"]["manifest_version"] == "2026.03-manifestation-v1"
            assert msg["frontend_contract"] == "render-only"
            print("Handshake received")

            # Send Intent
            websocket.send_json({"text": "Hello Aether", "correlation_id": "corr-client-1", "trace_id": "trace-client-1"})

            # Expect Stream
            received_types = []

            for _ in range(10): # Increased safety limit
                try:
                    msg = websocket.receive_json()
                    received_types.append(msg["type"])
                    print(f"Received: {msg['type']}")

                    if msg["type"] == "intent_detected" and msg["topic"] == "intent.ingress":
                        assert msg["directive_state"]["correlation_id"] == "corr-client-1"
                        assert msg["directive_state"]["trace_id"] == "trace-client-1"
                        assert msg["frontend_contract"] == "render-only"
                        assert msg["directive_state"]["manifest_version"] == "2026.03-manifestation-v1"
                    if msg["type"] == "manifestation":
                        assert msg["directive_state"]["correlation_id"] == "corr-client-1"
                        assert msg["directive_state"]["trace_id"] == "trace-client-1"
                        assert msg["directive_state"]["manifest_version"] == "2026.03-manifestation-v1"
                        break
                    if msg["type"] == "degradation":
                        break
                except Exception as e:
                    print(f"Receive Error: {e}")
                    break

            assert "intent_detected" in received_types
            assert any(event_type in received_types for event_type in ("manifestation", "degradation"))


def test_manifestation_bridge_payload_exposes_render_only_contract():
    event = AetherEvent(
        type=AetherEventType.STATE_UPDATE,
        topic="governance.decision",
        session_id="ae-test",
        correlation_id="corr-1",
        trace_id="trace-1",
        origin={"service": "governance", "subsystem": "kernel", "channel": "ae-test"},
        target={"service": "client", "subsystem": "manifestation", "channel": "ae-test"},
        payload={
            "status": "ALLOWED",
            "status_block": {"phase": "governance", "label": "ALLOWED"},
            "diagnostics": {"bridge": "ws_v3"},
        },
    )

    payload = _manifestation_bridge_payload(event, lifecycle_stage="governance_emit")

    assert payload["frontend_contract"] == "render-only"
    assert payload["semantic_source"] == "backend"
    assert payload["directive_state"]["manifest_version"] == "2026.03-manifestation-v1"
    assert payload["status"] == {"phase": "governance", "label": "ALLOWED"}
