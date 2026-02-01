from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from itsdangerous import URLSafeTimedSerializer
from typing import Optional
import secrets
from src.backend.core.config import settings
import logging
from .providers import get_auth_provider
from .session_manager import AuthManager

logger = logging.getLogger("AuthRoutes")
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize Managers
auth_manager = AuthManager()
signer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="logenesis-session")

COOKIE_NAME = "logenesis_session"

def get_current_user_id(request: Request) -> Optional[str]:
    """Extracts and verifies the user ID from the signed session cookie.

    Args:
        request: The FastAPI request object.

    Returns:
        The user ID string if the cookie is present and valid, otherwise None.
    """
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return None
    try:
        # max_age=14 days
        user_id = signer.loads(cookie, max_age=86400 * 14)
        return user_id
    except Exception:
        return None

@router.get("/login")
def login(request: Request):
    """Initiates the OAuth 2.0 login flow.

    Generates a state parameter for CSRF protection, sets it in a cookie,
    and redirects the user to the configured authentication provider.

    Args:
        request: The FastAPI request object.

    Returns:
        A RedirectResponse to the provider's login URL.
    """
    provider = get_auth_provider()
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(16)

    # In a real app, store state in a cookie/session to verify later
    # For now, we trust the provider redirect

    auth_url = provider.get_login_url(state=state)
    response = RedirectResponse(url=auth_url)

    # Store state in cookie to verify on callback
    response.set_cookie(key="oauth_state", value=state, httponly=True)

    return response

@router.get("/callback")
async def callback(request: Request):
    """Handles the OAuth 2.0 callback from the provider.

    Verifies the CSRF state, exchanges the authorization code for tokens,
    creates a user session, and sets a signed session cookie.

    Args:
        request: The FastAPI request object containing query parameters.

    Returns:
        A RedirectResponse to the root URL upon success.

    Raises:
        HTTPException: If the code is missing, state is invalid, or authentication fails.
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    stored_state = request.cookies.get("oauth_state")

    if not code:
        raise HTTPException(status_code=400, detail="Missing auth code")

    # CSRF Check
    # Mock provider might assume strict state handling or bypass
    if settings.AUTH_PROVIDER != "mock" and state != stored_state:
        logger.warning("CSRF State mismatch")
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    provider = get_auth_provider()
    try:
        identity, tokens = await provider.exchange_code(code)
    except Exception as e:
        logger.error(f"Auth Exchange Failed: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

    # Determine User ID
    user_id = identity.sub

    # Persist Session
    session = auth_manager.upsert_user(user_id, identity, tokens)

    # Create Signed Cookie
    signed_session_id = signer.dumps(user_id)

    # Redirect to App
    response = RedirectResponse(url="/") # Back to root
    response.set_cookie(
        key=COOKIE_NAME,
        value=signed_session_id,
        httponly=True,
        secure=False, # Set True in Prod with HTTPS
        samesite="lax",
        max_age=86400 * 14
    )
    response.delete_cookie("oauth_state")

    return response

@router.get("/me")
def get_me(request: Request):
    """Retrieves the current authenticated user's profile and state.

    Args:
        request: The FastAPI request object.

    Returns:
        A dictionary containing authentication status, user profile, and Logenesis state.
        Returns 401 status if not authenticated.
    """
    user_id = get_current_user_id(request)
    if not user_id:
        return JSONResponse({"authenticated": False}, status_code=401)

    session = auth_manager.get_user(user_id)
    if not session:
         return JSONResponse({"authenticated": False}, status_code=401)

    return {
        "authenticated": True,
        "user": session.identity.model_dump(),
        "logenesis_state": session.logenesis_state.model_dump()
    }

@router.get("/logout")
def logout():
    """Logs out the user.

    Clears the session cookie and redirects to the root.

    Returns:
        A RedirectResponse to the root URL.
    """
    response = RedirectResponse(url="/")
    response.delete_cookie(COOKIE_NAME)
    return response
