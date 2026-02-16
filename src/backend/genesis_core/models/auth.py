from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class IdentityProfile(BaseModel):
    """
    The verified identity of a Resonator, sourced from an external OIDC provider.
    """
    provider: str = Field(..., description="OAuth Provider name (e.g., 'google', 'mock')", examples=["google"])
    sub: str = Field(..., description="Unique Subject ID from the provider", examples=["108342190..."])
    email: Optional[str] = Field(None, description="Verified email address", examples=["user@example.com"])
    name: Optional[str] = Field(None, description="Display name of the user", examples=["John Doe"])
    picture: Optional[str] = Field(None, description="URL to the user profile image")

class TokenSet(BaseModel):
    """
    Security tokens for maintaining the established session.
    """
    access_token: str = Field(..., description="Bearer token for API access")
    refresh_token: Optional[str] = Field(None, description="Token used to obtain a new access token")
    expires_at: float = Field(..., description="Unix timestamp of token expiration", examples=[1700000000.0])

class LogenesisStateSummary(BaseModel):
    """
    Lightweight summary of the cognitive relationship between the user and the system.
    This summary influences AI-driven permission decisions.
    """
    trust_level: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="The calculated trust metric for this user based on behavioral history.",
        examples=[0.85]
    )
    resonance_profile: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value store of semantic alignment preferences."
    )
    interaction_count: int = Field(
        0,
        description="Total number of cognitive intents processed for this user.",
        examples=[142]
    )

class UserSession(BaseModel):
    """
    A persistent session record, linking a verified identity to a cognitive state.
    """
    user_id: str = Field(..., description="Internal unique identifier for the user.", examples=["usr_5a1e..."])
    identity: IdentityProfile
    tokens: TokenSet
    logenesis_state: LogenesisStateSummary = Field(
        default_factory=LogenesisStateSummary,
        description="The state summary used by agents like ValidatorAgent for contextual auditing."
    )
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())
    last_accessed: float = Field(default_factory=lambda: datetime.now().timestamp())

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "google-12345",
                "identity": {
                    "provider": "google",
                    "sub": "12345",
                    "email": "dev@aetherium.ai",
                    "name": "Lead Resonator"
                },
                "logenesis_state": {
                    "trust_level": 0.9,
                    "interaction_count": 500
                }
            }
        }
