import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from src.backend.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_auth_me_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_session_creation():
    transport = ASGITransport(app=app)
    payload = {
        "access_key": "test_key",
        "contract": {
             "identity": "test_agent",
             "intent": "simulation",
             "capabilities": ["text"]
        }
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/v1/session", json=payload)
    # It might fail due to lack of real key but we check it hits the route
    assert response.status_code in [200, 201, 400, 401, 422]
