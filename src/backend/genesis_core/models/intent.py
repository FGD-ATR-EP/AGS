from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class IntentContext(BaseModel):
    """
    Contextual metadata for the Intent, capturing the 'emotional' and 'energetic' state of the signal.
    """
    emotional_valence: float = Field(
        0.0,
        ge=-1.0,
        le=1.0,
        description="Sentiment of the intent. -1.0 (Very Negative) to 1.0 (Very Positive).",
        examples=[0.5]
    )
    energy_level: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Urgency or activation level of the intent. 0.0 (Idle) to 1.0 (High Urgency).",
        examples=[0.8]
    )
    turbulence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Degree of confusion or entropy in the signal. 0.0 (Clear) to 1.0 (Chaotic).",
        examples=[0.1]
    )
    source_confidence: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="The reliability of the originating source as perceived by the emitter.",
        examples=[0.95]
    )

class IntentPayload(BaseModel):
    """
    The core content of the intent. This represents the 'Firma' or concrete data of the signal.
    """
    content: Any = Field(
        ...,
        description="The primary data payload. Can be raw text, JSON objects, or serialized bytes.",
        examples=["Analyze the current system entropy."]
    )
    modality: str = Field(
        ...,
        description="The data format: 'text', 'image', 'audio', 'json', or 'mixed'.",
        examples=["text"]
    )
    encryption_level: str = Field(
        default="NONE",
        description="Cryptographic protection level applied to the content: 'NONE', 'AES-256', 'CHACHA20'.",
        examples=["NONE"]
    )

class SystemIntent(BaseModel):
    """
    The 'Intent Vector': The fundamental unit of communication across the AetherBus.
    It encapsulates both the 'Inspira' (Context/Will) and 'Firma' (Payload/Body).
    """
    vector_id: str = Field(
        default_factory=lambda: uuid.uuid4().hex,
        description="Immutable unique identifier for this specific intent transmission.",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp(),
        description="Unix timestamp marking the exact moment of emission with nanosecond precision.",
        examples=[1700000000.123456]
    )
    origin_agent: str = Field(
        ...,
        description="The unique identity name of the agent that generated this intent.",
        examples=["AgioSage_v1"]
    )
    target_agent: Optional[str] = Field(
        None,
        description="The intended recipient agent. If null, the intent is broadcast to all resonant agents.",
        examples=["ValidatorAgent"]
    )
    intent_type: str = Field(
        ...,
        description="The functional category: 'COGNITIVE_QUERY', 'MANIFESTATION_REQUEST', 'AUDIT_LOG', 'STATE_SYNC'.",
        examples=["COGNITIVE_QUERY"]
    )
    payload: IntentPayload
    context: IntentContext
    correlation_id: Optional[str] = Field(
        None,
        description="Links this intent to a previous one, forming a causal chain (e.g., a response to a query).",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"]
    )
    signature: Optional[str] = Field(
        None,
        description="HMAC or RSA signature ensuring the integrity and authenticity of the intent.",
        examples=["v1:sha256:abc..."]
    )

    class Config:
        frozen = True
        json_schema_extra = {
            "example": {
                "origin_agent": "User_Session_001",
                "intent_type": "COGNITIVE_QUERY",
                "payload": {
                    "content": "What is the status of the Akashic Treasury?",
                    "modality": "text"
                },
                "context": {
                    "emotional_valence": 0.1,
                    "energy_level": 0.4
                }
            }
        }
