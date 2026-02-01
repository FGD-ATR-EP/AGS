from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class IdentityProfile(BaseModel):
    provider: str
    sub: str = Field(..., description="Subject ID from Provider")
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None

class TokenSet(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: float  # Timestamp

class LogenesisStateSummary(BaseModel):
    """
    Lightweight summary of the cognitive state stored in the auth record.
    Full state is managed by the Engine.
    """
    trust_level: float = 0.5
    resonance_profile: Dict[str, Any] = Field(default_factory=dict)
    interaction_count: int = 0

class UserSession(BaseModel):
    user_id: str = Field(..., description="Unique Subject ID from Provider (e.g., google-123)")
    identity: IdentityProfile
    tokens: TokenSet
    logenesis_state: LogenesisStateSummary = Field(default_factory=LogenesisStateSummary)
    created_at: float
    last_accessed: float
