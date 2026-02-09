from enum import Enum
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

# --- Enums ---

class AetherEventType(str, Enum):
    # Core Lifecycle
    STATE_UPDATE = "state_update"         # Periodic internal state (heartbeat)
    INTENT_DETECTED = "intent_detected"   # Raw signal converted to intent
    CONFIDENCE_SHIFT = "confidence_shift" # Internal probability change
    RESONANCE_PEAK = "resonance_peak"     # High alignment/understanding
    MANIFESTATION = "manifestation"       # Final output (Text/Visual/Action)
    DEGRADATION = "degradation"           # Error, confusion, entropy increase
    SILENCE = "silence"                   # Idle / Listening

    # Control
    HANDSHAKE = "handshake"
    ERROR = "error"

class ResonanceForm(str, Enum):
    SPHERE = "sphere"     # ChitChat / Neutral
    CUBE = "cube"         # Analytic
    VORTEX = "vortex"     # Creative / High Energy
    GRID = "grid"         # System / Low Energy
    NEBULA = "nebula"     # Ambiguous / Thinking

# --- Data Models ---

class IntentVector(BaseModel):
    """
    The mathematical representation of an intent.
    Used for resonance calculation and visualization.
    """
    clarity: float = Field(..., ge=0.0, le=1.0, description="How clear the intent is")
    emotional_valence: float = Field(..., ge=-1.0, le=1.0, description="Positive vs Negative sentiment")
    urgency: float = Field(..., ge=0.0, le=1.0, description="Priority level")
    trust: float = Field(..., ge=0.0, le=1.0, description="Source reliability or internal confidence")

class IntentData(BaseModel):
    """
    The semantic payload of an intent.
    """
    vector: IntentVector
    semantic_hint: Optional[str] = Field(None, description="Short text label (e.g. 'agreement', 'query')")
    raw_content: Optional[str] = Field(None, description="Original text if applicable (optional)")

class ManifestationData(BaseModel):
    """
    The crystallized output of the system.
    """
    intent: str = Field(..., description="Category (e.g., acknowledgement, answer)")
    resonance: float = Field(..., ge=0.0, le=1.0)
    form: ResonanceForm
    color: str = Field(..., description="Hex code or color name")
    content: Union[str, Dict[str, Any]] = Field(..., description="The actual message/data")

class StateData(BaseModel):
    """
    Internal system state snapshot.
    """
    state: str = Field(..., description="Current operational mode (e.g. 'thinking', 'idle')")
    confidence: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    coherence: float = Field(..., ge=0.0, le=1.0, description="Internal logic consistency")

# --- The Envelope ---

class AetherEvent(BaseModel):
    """
    The standard message format for the Aetherium Data Plane.
    """
    type: AetherEventType
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    session_id: Optional[str] = None

    # One of these fields should be populated based on type
    state: Optional[StateData] = None
    manifestation: Optional[ManifestationData] = None
    intent: Optional[IntentData] = None
    error: Optional[str] = None
    extensions: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
        extra = "ignore"
