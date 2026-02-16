from enum import Enum
from typing import Optional, Dict, Any, Union, List
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

    # Control & Security
    HANDSHAKE = "handshake"
    ERROR = "error"
    AUDIT_LOG = "audit_log"               # Security and permission audit events
    HEALTH_SIGNAL = "health_signal"       # System health and scaling metrics

class ResonanceForm(str, Enum):
    SPHERE = "sphere"     # ChitChat / Neutral
    CUBE = "cube"         # Analytic
    VORTEX = "vortex"     # Creative / High Energy
    GRID = "grid"         # System / Low Energy
    NEBULA = "nebula"     # Ambiguous / Thinking

class AuditSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    PARAJIKA = "parajika" # Terminal system violation

# --- Data Models ---

class IntentVector(BaseModel):
    """
    Mathematical representation of an intent for resonance calculation and visualization.
    """
    clarity: float = Field(..., ge=0.0, le=1.0, description="Semantic clarity (0.0 to 1.0)", examples=[0.9])
    emotional_valence: float = Field(..., ge=-1.0, le=1.0, description="Sentiment (-1.0 to 1.0)", examples=[0.2])
    urgency: float = Field(..., ge=0.0, le=1.0, description="Priority (0.0 to 1.0)", examples=[0.5])
    trust: float = Field(..., ge=0.0, le=1.0, description="Source reliability (0.0 to 1.0)", examples=[1.0])

class IntentData(BaseModel):
    """
    Semantic payload of a detected intent.
    """
    vector: IntentVector
    semantic_hint: Optional[str] = Field(None, description="Short label for the intent", examples=["query"])
    raw_content: Optional[str] = Field(None, description="Original source text", examples=["Hello World"])

class ManifestationData(BaseModel):
    """
    The crystallized output of the system (The 'Result').
    """
    intent: str = Field(..., description="Output category", examples=["answer"])
    resonance: float = Field(..., ge=0.0, le=1.0, description="Final coherence level")
    form: ResonanceForm = Field(..., description="Geometric representation form")
    color: str = Field(..., description="Visual resonance color (Hex)", examples=["#00ffcc"])
    content: Union[str, Dict[str, Any]] = Field(..., description="The actual response data")

class StateData(BaseModel):
    """
    Internal system state snapshot.
    """
    state: str = Field(..., description="Operational mode", examples=["thinking"])
    confidence: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    coherence: float = Field(..., ge=0.0, le=1.0)

class AuditData(BaseModel):
    """
    Security and Governance audit record.
    """
    actor: str = Field(..., description="The entity performing the action", examples=["ValidatorAgent"])
    action: str = Field(..., description="The action being audited", examples=["PERMISSION_CHECK"])
    target: str = Field(..., description="The resource or agent affected", examples=["AkashicRecords"])
    severity: AuditSeverity = Field(default=AuditSeverity.INFO)
    outcome: str = Field(..., description="Success, Denied, or Flagged", examples=["ALLOWED"])
    reasoning: Optional[str] = Field(None, description="AI-generated justification for the decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context (e.g. risk scores)")

# --- The Envelope ---

class AetherEvent(BaseModel):
    """
    Standard message format for the AetherBus Data Plane.
    """
    type: AetherEventType = Field(..., description="The category of the event")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="Unix timestamp")
    session_id: Optional[str] = Field(None, description="The session or agent ID context")

    # Payload fields (optional depending on type)
    state: Optional[StateData] = None
    manifestation: Optional[ManifestationData] = None
    intent: Optional[IntentData] = None
    audit: Optional[AuditData] = None
    error: Optional[str] = None
    extensions: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata for external expansion")

    class Config:
        use_enum_values = True
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "type": "manifestation",
                "session_id": "ae-789",
                "manifestation": {
                    "intent": "greeting",
                    "resonance": 0.95,
                    "form": "sphere",
                    "color": "#06b6d4",
                    "content": "Hello, Resonator."
                }
            }
        }
