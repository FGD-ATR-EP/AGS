from pydantic import BaseModel
from typing import Optional, Tuple, List, Dict
from enum import Enum, IntEnum

class LightAction(str, Enum):
    """
    Defines the atomic operations allowed within the LightProtocol.
    """
    SPAWN = "SPAWN"
    MOVE = "MOVE"
    ERASE = "ERASE"
    EMPHASIZE = "EMPHASIZE"
    MANIFEST = "MANIFEST"  # Added for image formation
    ANSWER = "ANSWER"      # Added for pure text response

class TemporalType(str, Enum):
    INSTANT = "instant"
    CONTINUOUS = "continuous"

class PriorityLevel(IntEnum):
    AMBIENT = 0
    USER = 1
    SAFETY = 2
    SYSTEM = 3

class LightIntent(BaseModel):
    """
    A structured signal within the LightProtocol.
    Represents a discrete cognitive intent to be rendered as an observable event.
    """
    action: LightAction
    target: Optional[str] = None
    region: Optional[Tuple[float, float, float, float]] = None # normalized bbox
    vector: Optional[Tuple[float, float]] = None # direction
    intensity: Optional[float] = None
    color_hint: Optional[str] = None
    decay: Optional[float] = None
    temporal: Optional[TemporalType] = None
    priority: int = PriorityLevel.USER
    source: str = "unknown"
    # Added for MANIFEST intent payload (list of particle targets)
    # Format: [(x, y, color_hex), ...]
    formation_data: Optional[List[Tuple[float, float, str]]] = None
    # Added for high-level shape requests (e.g. "circle")
    shape_name: Optional[str] = None
    text_content: Optional[str] = None

class LightInstruction(BaseModel):
    intent: LightAction
    target: Optional[str] = None
    vector: Optional[Tuple[float, float]] = None
    strength: Optional[float] = None
    decay: Optional[float] = None
    shape: Optional[str] = None
    region: Optional[Tuple[float, float, float, float]] = None
    motion: Optional[str] = None
    color_profile: Optional[str] = None
    text_content: Optional[str] = None
    # Added to carry calculated points to the client
    formation_data: Optional[List[Tuple[float, float, str]]] = None

class LightEntity(BaseModel):
    id: str
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    energy: float
    history: List[Tuple[float, float]] = []
    # Physics target for formation
    target_position: Optional[Tuple[float, float]] = None
    target_color: Optional[str] = None

class LightState(BaseModel):
    entities: Dict[str, LightEntity]
    system_energy: float
