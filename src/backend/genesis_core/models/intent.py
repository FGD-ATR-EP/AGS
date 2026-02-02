from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class IntentContext(BaseModel):
    """
    Contextual metadata for the Intent.
    """
    emotional_valence: float = Field(0.0, description="Positive/Negative sentiment (-1.0 to 1.0)")
    energy_level: float = Field(0.0, description="Urgency/Intensity (0.0 to 1.0)")
    turbulence: float = Field(0.0, description="Entropy/Confusion (0.0 to 1.0)")
    source_confidence: float = Field(1.0, description="Confidence of the origin agent")

class IntentPayload(BaseModel):
    """
    The content of the intent. PII should be removed before packing here.
    """
    content: Any = Field(..., description="The actual data (text, image bytes, object)")
    modality: str = Field(..., description="text, image, audio, mixed")
    encryption_level: str = Field(default="NONE", description="NONE, AES, CHACHA20")

class SystemIntent(BaseModel):
    """
    The 'Intent Vector' as defined in the Aetherium-Genesis Blueprint.
    Used for inter-agent communication via AetherBus.
    """
    vector_id: str = Field(default_factory=lambda: uuid.uuid4().hex, description="Unique Hash ID")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="Unix timestamp with ns precision")
    origin_agent: str = Field(..., description="Name of the sender agent")
    target_agent: Optional[str] = Field(None, description="Specific target or None for broadcast")
    intent_type: str = Field(..., description="COGNITIVE_QUERY, MANIFESTATION_REQUEST, etc.")
    payload: IntentPayload
    context: IntentContext
    correlation_id: Optional[str] = Field(None, description="ID of the intent being replied to")
    signature: Optional[str] = Field(None, description="HMAC Signature for integrity")

    class Config:
        frozen = True # Make it immutable hashable-like if needed, though Pydantic frozen is distinct
