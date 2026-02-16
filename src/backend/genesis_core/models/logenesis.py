from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
try:
    import torch
    Tensor = torch.Tensor
except ImportError:
    torch = None
    Tensor = Any

from .light import LightIntent
from .visual import VisualParameters

@dataclass
class IntentPacket:
    modality: Literal["text", "visual"]
    embedding: Optional[Tensor]
    energy_level: float
    confidence: float
    raw_payload: Any

class LogenesisState(str, Enum):
    VOID = "VOID"           # Initial unmanifested state
    AWAKENED = "AWAKENED"   # Active cognitive processing
    NIRODHA = "NIRODHA"     # Peak state of focused stillness
    COLLAPSED = "COLLAPSED" # Failure or high entropy state

class StateMetrics(BaseModel):
    """
    Measurable dimensions of the system's internal cognitive physics.
    Used for monitoring the 'Health of Thought'.
    """
    intent_entropy: float = Field(..., ge=0.0, le=1.0, description="Internal conflict level (0.0=Crystal Clear, 1.0=Chaos)", examples=[0.12])
    temporal_coherence: float = Field(..., ge=0.0, le=1.0, description="Logical continuity from previous state (0.0=Disjoint, 1.0=Fluid)", examples=[0.88])
    structural_stability: float = Field(..., ge=0.0, le=1.0, description="Overall system integrity (0.0=Collapse, 1.0=Stable)", examples=[0.95])

class IntentVector(BaseModel):
    """
    Mathematical representation of the user's latent intent.
    Used by ARL (Adaptive Resonance Logic) to calculate resonance scores and drive NPC behavior.
    """
    epistemic_need: float = Field(..., ge=0.0, le=1.0, description="Need for raw knowledge/facts.", examples=[0.7])
    subjective_weight: float = Field(..., ge=0.0, le=1.0, description="Weight of subjective/contextual factors.", examples=[0.3])
    decision_urgency: float = Field(..., ge=0.0, le=1.0, description="Need for immediate decision/action.", examples=[0.2])
    precision_required: float = Field(..., ge=0.0, le=1.0, description="Need for precise/formal structure.", examples=[0.9])
    raw_embedding: Optional[List[float]] = Field(default=None, description="Mock 512-dim vector for high-dimensional analysis.")

class ExpressionState(BaseModel):
    """
    The persistent 'Trajectory' of the AI's expression for a specific session.
    This replaces static 'Personas'. It drifts based on interaction pressure.
    """
    current_vector: IntentVector = Field(..., description="The current smoothed expression vector")
    previous_vector: Optional[IntentVector] = Field(default=None, description="The vector from the previous time step")
    velocity: float = Field(default=0.0, description="Rate of change in the vector (Volatility)")
    inertia: float = Field(default=0.8, description="Current resistance to change (0.1=Fluid, 0.9=Rigid)")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last interaction timestamp")

class VisualQualia(BaseModel):
    """
    Non-verbal communication parameters representing the 'Light' Language.
    Directly affects the GunUI particle engine.
    """
    color: str = Field(..., description="Hex color code representing the intent resonance.", examples=["#A855F7"])
    intensity: float = Field(..., ge=0.0, le=1.0, description="Brightness/Opacity of the visualization.")
    turbulence: float = Field(..., ge=0.0, le=1.0, description="Chaos factor: 0.0=Still, 1.0=Violent Storm.")
    shape: str = Field(default="nebula", description="Target shape topology: nebula, shard, orb, void.", examples=["orb"])

class AudioQualia(BaseModel):
    """
    Sonic parameters for embodied reasoning.
    """
    rhythm_density: float = Field(..., ge=0.0, le=1.0, description="Density of rhythmic events.")
    tone_texture: str = Field(..., description="Texture of the sound: smooth, granular, noise-like.", examples=["granular"])
    amplitude_bias: float = Field(..., ge=0.0, le=1.0, description="Base amplitude/volume bias.")

class PhysicsParams(BaseModel):
    """
    Direct instructions for the GunUI particle engine (Firma Layer).
    """
    spawn_rate: int = Field(default=0, description="Particles to spawn per frame/tick.", examples=[50])
    velocity_bias: List[float] = Field(default_factory=lambda: [0.0, 0.0], description="[x, y] flow bias for particles.")
    decay_rate: float = Field(default=0.01, description="How fast particles fade from existence.")

class LogenesisResponse(BaseModel):
    """
    The holistic response packet from LOGENESIS Engine.
    Combines verbal (text) and non-verbal (visual/audio/physics) signals into a unified manifestation.
    """
    type: str = Field("LOGENESIS_RESPONSE", description="Response type identifier.")
    state: LogenesisState = Field(..., description="Current state of the Logenesis cycle.")
    text_content: Optional[str] = Field(None, description="Verbalized response from the Sage.", examples=["The system state is stable."])
    visual_qualia: Optional[VisualQualia] = None
    audio_qualia: Optional[AudioQualia] = None
    physics_params: Optional[PhysicsParams] = None
    intent_debug: Optional[IntentVector] = None
    state_metrics: Optional[StateMetrics] = None
    manifestation_granted: bool = Field(default=True, description="Whether the ValidatorAgent permitted this manifestation.")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "LOGENESIS_RESPONSE",
                "state": "AWAKENED",
                "text_content": "Query processed successfully.",
                "visual_qualia": {
                    "color": "#06b6d4",
                    "intensity": 0.8,
                    "turbulence": 0.1,
                    "shape": "sphere"
                },
                "state_metrics": {
                    "intent_entropy": 0.05,
                    "temporal_coherence": 0.98,
                    "structural_stability": 1.0
                }
            }
        }
