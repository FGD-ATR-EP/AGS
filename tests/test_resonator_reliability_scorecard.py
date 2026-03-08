from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.routers.metrics import (
    MetricCollector,
    ResonatorReliabilityTracker,
    ResonatorTelemetryPoint,
)


def test_resonator_scorecard_daily_and_weekly_windows():
    tracker = ResonatorReliabilityTracker()
    now = datetime.now()

    tracker.record(
        ResonatorTelemetryPoint(
            resonator_id="res-1",
            latency_ms=120.0,
            correction_rate=0.10,
            safety_override_triggered=False,
            timestamp=now - timedelta(hours=2),
        )
    )
    tracker.record(
        ResonatorTelemetryPoint(
            resonator_id="res-1",
            latency_ms=220.0,
            correction_rate=0.20,
            safety_override_triggered=True,
            timestamp=now - timedelta(hours=4),
        )
    )

    scorecard = tracker.get_scorecard()

    assert "res-1" in scorecard
    assert scorecard["res-1"]["daily"]["samples"] == 2
    assert scorecard["res-1"]["weekly"]["samples"] == 2
    assert scorecard["res-1"]["daily"]["avg_latency_ms"] == 170.0
    assert scorecard["res-1"]["daily"]["avg_correction_rate"] == 0.15
    assert 0.0 <= scorecard["res-1"]["daily"]["reliability_score"] <= 100.0


def test_resonator_scorecard_excludes_older_than_week():
    tracker = ResonatorReliabilityTracker()
    now = datetime.now()

    tracker.record(
        ResonatorTelemetryPoint(
            resonator_id="res-2",
            latency_ms=100.0,
            correction_rate=0.05,
            timestamp=now - timedelta(days=8),
        )
    )
    tracker.record(
        ResonatorTelemetryPoint(
            resonator_id="res-2",
            latency_ms=200.0,
            correction_rate=0.25,
            timestamp=now - timedelta(hours=3),
        )
    )

    scorecard = tracker.get_scorecard()

    assert scorecard["res-2"]["daily"]["samples"] == 1
    assert scorecard["res-2"]["weekly"]["samples"] == 1
    assert scorecard["res-2"]["weekly"]["avg_latency_ms"] == 200.0


def test_resonator_reliability_api_endpoints():
    MetricCollector._instance = None
    with TestClient(app) as client:
        payload = {
            "resonator_id": "res-api-1",
            "latency_ms": 180.0,
            "correction_rate": 0.12,
            "safety_override_triggered": True,
        }
        ingest = client.post("/v1/metrics/resonator-telemetry", json=payload)
        assert ingest.status_code == 200

        report = client.get("/v1/metrics/resonator-reliability", params={"resonator_id": "res-api-1"})
        assert report.status_code == 200
        data = report.json()
        assert data["resonator_id"] == "res-api-1"
        assert data["scorecard"]["daily"]["samples"] == 1

        missing = client.get("/v1/metrics/resonator-reliability", params={"resonator_id": "missing"})
        assert missing.status_code == 404
