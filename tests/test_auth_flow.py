from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.core.config import settings
import os

# Force Mock Mode
settings.AUTH_PROVIDER = "mock"
# Ensure the redirect URI matches what the mock provider expects/generates
# In the mock provider code: return f"{settings.GOOGLE_REDIRECT_URI}?..."
settings.GOOGLE_REDIRECT_URI = "http://testserver/auth/callback"

client = TestClient(app)

def test_auth_lifecycle():
    # 1. Test Login Redirect
    print("\n[TEST] 1. Initiating Login...")
    response = client.get("/auth/login", follow_redirects=False)

    # It should redirect. 307 is default for FastAPI RedirectResponse
    assert response.status_code == 307
    location = response.headers["location"]
    print(f"[TEST] Redirect Location: {location}")

    assert "code=mock_auth_code" in location
    assert "state=" in location

    # Extract state for the callback (though mock might ignore it, the route checks it)
    # Actually route checks cookie vs param.
    # When using TestClient, cookies set in response are saved to client.

    # 2. Test Callback
    # The location is the full URL the user would be sent to.
    # In a real browser, the browser goes there.
    # The mock provider returns the callback URL directly.
    callback_url = location

    print("[TEST] 2. Following Callback...")
    # We follow the redirect manually to inspect headers if needed,
    # but client.get(callback_url) works.
    response = client.get(callback_url, follow_redirects=False)

    # Successful login redirects to root "/"
    assert response.status_code == 307
    assert response.headers["location"] == "/"
    assert "logenesis_session" in client.cookies
    print("[TEST] Session Cookie Set.")

    # 3. Test /auth/me (Authenticated)
    print("[TEST] 3. Checking /auth/me...")
    response = client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["authenticated"] is True
    assert data["user"]["email"] == "traveler@logenesis.local"
    print(f"[TEST] User Verified: {data['user']['email']}")

    # 4. Test Logout
    print("[TEST] 4. Logging Out...")
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}

    # 5. Verify Logout
    print("[TEST] 5. Verifying Logout...")
    # Cookie should be cleared or invalid
    response = client.get("/auth/me")
    # The route returns 401 if not authenticated
    assert response.status_code == 401
    print("[TEST] Auth Cycle Complete.")
