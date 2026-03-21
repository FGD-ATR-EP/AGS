from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from src.backend.genesis_core.entropy.schemas import EntropyPacket
from src.backend.genesis_core.entropy.service import EntropyValidator
from src.backend.main import app


def _packet(confidence: float, action_type: str = "creative_writing", preview: str = "sunrise folds into code"):
    return {
        "packet_id": str(uuid4()),
        "timestamp": "2023-10-27T10:00:00Z",
        "user_context": {
            "current_screen": "dashboard",
            "previous_actions": ["click_home", "scroll_down"],
        },
        "prediction_snapshot": {
            "model_version": "CSP-X1-Beta",
            "predicted_action": "click_notification",
            "confidence_score": confidence,
        },
        "actual_action": {
            "type": action_type,
            "content_hash": "sha256_of_content",
            "input_method": "voice_dictation",
            "content_preview": preview,
            "micro_metrics": {
                "typing_variance": 0.6,
                "hesitation_pauses": 2,
                "mouse_jitter": 0.4,
            },
        },
    }


def test_validator_filters_noise_to_zero_qou():
    validator = EntropyValidator()
    packet = EntropyPacket.model_validate(_packet(0.2, action_type="keyboard_smash", preview="asdfasdfasdf"))

    assessment = validator.assess(packet)

    assert assessment.semantic_weight == 0.0
    assert assessment.qou_score == 0.0
    assert assessment.reward_amount == 0


def test_entropy_submit_returns_preserve_artifact_on_high_qou():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/entropy/submit",
            json={
                "user_id": str(uuid4()),
                "packet": _packet(0.05, preview="abcdefghijklmnopqrstuvwxyz"),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["assessment"]["qou_score"] > 0.8
    assert body["assessment"]["meter_state"] == "chaotic_genius"
    assert body["assessment"]["preserve"] is True
    assert body["artifact_ref"].startswith("akashic://entropy/")


def test_ledger_explorer_filters_by_time_and_bands_and_reports_continuity():
    with TestClient(app) as client:
        low_user = str(uuid4())
        medium_user = str(uuid4())
        high_user = str(uuid4())

        low_res = client.post(
            "/api/v1/entropy/submit",
            json={
                "user_id": low_user,
                "packet": _packet(0.95, preview="quiet"),
            },
        )
        medium_res = client.post(
            "/api/v1/entropy/submit",
            json={
                "user_id": medium_user,
                "packet": _packet(0.5, preview="signal"),
            },
        )
        high_res = client.post(
            "/api/v1/entropy/submit",
            json={
                "user_id": high_user,
                "packet": _packet(0.02, preview="abcdefghijklmnopqrstuvwxyz"),
            },
        )

        assert low_res.status_code == 200
        assert medium_res.status_code == 200
        assert high_res.status_code == 200

        entries = app.state.akashic_treasury.entries
        now = datetime.now(UTC)
        entries[0].created_at = now - timedelta(minutes=30)
        entries[1].created_at = now - timedelta(minutes=10)
        entries[2].created_at = now

        start = (now - timedelta(minutes=20)).isoformat()
        end = (now + timedelta(minutes=1)).isoformat()

        response = client.get(
            "/api/v1/entropy/ledger/explorer",
            params={
                "start_time": start,
                "end_time": end,
                "qou_bands": ["medium", "high"],
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_entries"] == 2
    assert body["continuity"]["checked_entries"] == 2
    assert body["continuity"]["contiguous"] is False
    assert any(issue["issue"] == "hash_self_integrity_failure" for issue in body["continuity"]["issues"])
    assert {entry["qou_band"] for entry in body["entries"]} == {"medium", "high"}


def test_ledger_explorer_rejects_invalid_time_range():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/entropy/ledger/explorer",
            params={
                "start_time": "2024-01-01T10:00:00Z",
                "end_time": "2024-01-01T09:00:00Z",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "start_time must be <= end_time"


def test_entropy_replay_returns_documents_timeline_and_explanation():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/entropy/replay",
            json={
                "user_id": str(uuid4()),
                "packet": _packet(0.02, preview="novel symbolic synthesis output"),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["assessment"]["qou_score"] > 0.3
    assert len(body["documents"]) == 4
    assert len(body["timeline"]) == 5
    assert body["explanation"]["quality_band"] in {"medium", "high"}
    assert body["timeline"][0]["label"] == "Predict"


def test_entropy_replay_rejects_invalid_packet_payload():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/entropy/replay",
            json={
                "user_id": str(uuid4()),
                "packet": {
                    **_packet(0.3),
                    "prediction_snapshot": {
                        "model_version": "CSP-X1-Beta",
                        "predicted_action": "click_notification",
                        "confidence_score": 1.5,
                    },
                },
            },
        )

    assert response.status_code == 422
