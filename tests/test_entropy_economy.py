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
