import pytest
import sys
import os
from unittest.mock import MagicMock

# Ensure path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.genesis_core.auditorium.dashboard import AetheriumHealthDashboard
from src.backend.genesis_core.auditorium.service import AuditoriumService
from src.backend.genesis_core.logenesis.engine import LogenesisEngine

@pytest.mark.asyncio
async def test_dashboard_instantiation():
    mock_engine = MagicMock()
    # Mock attributes expected by auditors
    mock_engine.last_visual_params = {}
    mock_engine.current_intent = "test"
    mock_engine.current_action = "test"

    dashboard = AetheriumHealthDashboard(mock_engine)
    assert dashboard.memory is not None
    assert dashboard.bus is not None

    report = await dashboard.generate_comprehensive_report()
    assert "timestamp" in report
    assert "overall_health_score" in report
    assert "components" in report

    # Check if scores are calculated
    assert report["overall_health_score"] >= 0.0

@pytest.mark.asyncio
async def test_service_lifecycle():
    mock_engine = MagicMock()
    service = AuditoriumService(mock_engine)

    service.start()
    assert service.running
    assert service.task is not None

    await service.stop()
    assert not service.running

def test_engine_suspend():
    # This might require API key or mock
    # LogenesisEngine init checks env var.
    # We should mock it or ensure it doesn't crash.
    # The LogenesisEngine init uses settings.GOOGLE_API_KEY

    try:
        engine = LogenesisEngine()
        resp = engine.suspend()
        # State is an Enum
        assert engine.state.name == "NIRODHA"
        assert "NIRODHA" in resp.text_content
    except Exception as e:
        pytest.fail(f"Engine Init failed: {e}")


def test_bus_auditor_close_releases_resources():
    from src.backend.genesis_core.auditorium.bus_audit import AetherBusAuditor

    auditor = AetherBusAuditor()
    writer = MagicMock()
    reader = MagicMock()
    auditor.writer = writer
    auditor.reader = reader

    auditor.close()

    reader.close.assert_called_once()
    writer.close.assert_called_once()
    assert auditor.reader is None
    assert auditor.writer is None
