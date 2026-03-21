from fastapi.testclient import TestClient

from src.backend.main import app


def test_homepage_reflects_governed_ai_os_architecture():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Governed AI-OS" in response.text
    assert "Canonical Control Loop" in response.text
    assert "Open Operations Dashboard" in response.text
    assert "AetherBus-Tachyon" in response.text
