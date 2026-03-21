from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

class CorrectionAction(Enum):
    MOVE = "move"
    ERASE = "erase"
    REDRAW = "redraw"
    EMPHASIZE = "emphasize"
    LOCK = "lock"

class StructuralGuide(Enum):
    TILE = "tile"
    EDGE = "canny"
    DEPTH = "depth"

@dataclass(frozen=True)
class SpatialMask:
    x_min: int
    y_min: int
    x_max: int
    y_max: int

@dataclass
class CorrectionEvent:
    event_id: str
    session_id: str
    timestamp: float
    affected_region: SpatialMask
    action_type: CorrectionAction
    intent_vector: List[float]          # [dx, dy, strength, ...]
    mode: str = "short_decay"           # "short_decay" or "persistent"
