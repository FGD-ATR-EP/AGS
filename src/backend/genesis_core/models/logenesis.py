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
    VOID = "VOID"
    AWAKENED = "AWAKENED"
    NIRODHA = "NIRODHA"
    COLLAPSED = "COLLAPSED"

class StateMetrics(BaseModel):
    """
    Measurable dimensions of the system's internal cognitive physics.
    """
    intent_entropy: float = Field(..., description="Internal conflict level (0.0=Crystal Clear, 1.0=Chaos)")
    temporal_coherence: float = Field(..., description="Logical continuity from previous state (0.0=Disjoint, 1.0=Fluid)")
    structural_stability: float = Field(..., description="Overall system integrity (0.0=Collapse, 1.0=Stable)")

class IntentVector(BaseModel):
    """
    Mathematical representation of the user's latent intent.
    Used by ARL (Adaptive Resonance Logic) to calculate resonance scores.
    """
    epistemic_need: float = Field(..., description="Need for raw knowledge/facts (0.0-1.0)")
    subjective_weight: float = Field(..., description="Weight of subjective/contextual factors (0.0-1.0). Replaces emotional_load.")
    decision_urgency: float = Field(..., description="Need for immediate decision/action (0.0-1.0)")
    precision_required: float = Field(..., description="Need for precise/formal structure (0.0-1.0)")
    # Simulation of high-dimensional embedding
    raw_embedding: Optional[List[float]] = Field(default=None, description="Mock 512-dim vector")

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
    Non-verbal communication parameters (The 'Light' Language).
    """
    color: str = Field(..., description="Hex color code, e.g., #A855F7")
    intensity: float = Field(..., description="Brightness/Opacity (0.0-1.0)")
    turbulence: float = Field(..., description="Chaos factor: 0.0=Still, 1.0=Violent Storm")
    shape: str = Field(default="nebula", description="Target shape topology: nebula, shard, orb, void")

class AudioQualia(BaseModel):
    """
    Sonic parameters for embodied reasoning.
    """
    rhythm_density: float = Field(..., description="Density of rhythmic events (0.0=Sparse/Ambient, 1.0=Dense/Tense)")
    tone_texture: str = Field(..., description="Texture of the sound: smooth, granular, noise-like")
    amplitude_bias: float = Field(..., description="Base amplitude/volume bias (0.0-1.0)")

class PhysicsParams(BaseModel):
    """
    Direct instructions for the GunUI particle engine.
    """
    spawn_rate: int = Field(default=0, description="Particles to spawn per frame/tick")
    velocity_bias: List[float] = Field(default_factory=lambda: [0.0, 0.0], description="[x, y] flow bias")
    decay_rate: float = Field(default=0.01, description="How fast particles fade")

class MemoryIndexItem(BaseModel):
    """
    Metadata for a memory item stored on the client.
    Sent to the server to check for relevance without revealing full content.
    """
    id: str = Field(..., description="Unique identifier for the memory")
    topic: str = Field(..., description="The main topic/keyword")
    timestamp: datetime = Field(..., description="When this memory was created")
    confidence: float = Field(default=1.0, description="Relevance score (client-side)")

class RecallProposal(BaseModel):
    """
    A proposal from the server to the user to recall a specific memory.
    """
    memory_id: str = Field(..., description="The ID of the memory to recall")
    topic: str = Field(..., description="The topic being recalled")
    reasoning: str = Field(..., description="Why the system suggests recalling this (e.g., 'You mentioned X...')")
    question: str = Field(..., description="The text to display to the user (e.g., 'Do you want to recall...?')")

class GenesisMemory(BaseModel):
    """
    Immutable core memory that defines the system's soul.
    "Jarum" (Inscribed) memories that persist across all sessions.
    """
    id: str = Field(..., description="Unique ID for the genesis memory")
    text_content: str = Field(..., description="The poetic/philosophical text")
    ideal_vector: IntentVector = Field(..., description="The perfect state vector associated with this memory")
    inscribed_at: datetime = Field(default_factory=datetime.now)

class LogenesisResponse(BaseModel):
    """
    The holistic response packet from LOGENESIS Engine.
    Combines verbal (text) and non-verbal (visual/audio/physics) signals.
    """
    type: str = "LOGENESIS_RESPONSE"
    state: LogenesisState
    text_content: Optional[str] = None
    visual_qualia: Optional[VisualQualia] = None
    audio_qualia: Optional[AudioQualia] = None
    physics_params: Optional[PhysicsParams] = None
    intent_debug: Optional[IntentVector] = None  # For testbed visualization
    state_metrics: Optional[StateMetrics] = None # The physics of thought report
    recall_proposal: Optional[RecallProposal] = None # Proposed memory recall handshake
    light_intent: Optional[LightIntent] = None # Direct bridge to LCL
    visual_analysis: Optional[VisualParameters] = None # New high-fidelity intent vector
    manifestation_granted: bool = Field(default=True, description="Whether the Manifestation Gate permitted this intent to be visualized")
