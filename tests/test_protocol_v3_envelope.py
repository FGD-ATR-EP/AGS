from src.backend.genesis_core.bus.base import BaseAetherBus
from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType


def test_v3_envelope_upgrades_legacy_event_shape():
    event = AetherEvent(
        type=AetherEventType.STATE_UPDATE,
        session_id="session-123",
        state={"state": "connected", "confidence": 1.0, "energy": 1.0, "coherence": 1.0},
    )

    assert event.envelope_version == "3.0.0"
    assert event.protocol_version == "2026.03"
    assert event.correlation_id == "session-123"
    assert event.topic == "session-123"
    assert event.payload["state"]["state"] == "connected"
    assert event.extensions["bus_metadata"]["codec"] == event.content.codec


def test_bus_validation_rejects_non_v3_envelope():
    event = AetherEvent(
        type=AetherEventType.HANDSHAKE,
        topic="manifestation.handshake",
        origin={"service": "api"},
        target={"service": "client"},
        payload={},
    )
    event.envelope_version = "2.0.0"

    try:
        BaseAetherBus.validate_event(event, stage="unit_test")
    except ValueError as exc:
        assert "Unsupported envelope_version" in str(exc)
    else:
        raise AssertionError("Expected validation failure for non-V3 envelope")



from src.backend.genesis_core.protocol.correlation import CorrelationPolicy


def test_correlation_policy_builds_trace_metadata():
    metadata = CorrelationPolicy.build(session_id="session-abc")

    assert metadata["correlation_id"] == "session-abc"
    assert metadata["trace_id"] == "session-abc"
    assert metadata["causation_id"] is None


def test_manifestation_directive_payload_preserves_backend_only_semantics():
    event = AetherEvent(
        type=AetherEventType.MANIFESTATION,
        topic="manifestation.response",
        origin={"service": "genesis_core", "subsystem": "mind"},
        target={"service": "client", "subsystem": "manifestation", "channel": "ae-123"},
        payload={
            "directive_state": {"lifecycle_stage": "manifestation_emit"},
            "render_state": {"template": "status_card"},
            "status": {"phase": "ready"},
            "replay": {"enabled": True},
            "diagnostics": {"bridge": "ws_v3"},
        },
    )

    directive_state = event.payload["directive_state"]
    assert directive_state["correlation_id"] == event.correlation_id
    assert directive_state["trace_id"] == event.trace_id
    assert directive_state["topic"] == "manifestation.response"
    assert directive_state["directive_type"] == "manifestation"
    assert directive_state["manifest_version"] == "2026.03-manifestation-v1"
