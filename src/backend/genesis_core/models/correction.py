from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum

class CorrectionAction(Enum):
    MOVE = "move"
    ERASE = "erase"
    REDRAW = "redraw"
    EMPHASIZE = "emphasize"

@dataclass(frozen=True)
class SpatialMask:
    """พื้นที่ที่ผู้ใช้แก้ไข (bounding box หรือ mask coordinates)"""
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    # หรือใช้ polygon points ถ้าต้องการ precision สูง

@dataclass
class CorrectionEvent:
    """เหตุการณ์แก้ไขหลัก — session-bound เท่านั้น"""
    event_id: str                   # uuid
    session_id: str
    timestamp: float
    affected_region: SpatialMask
    action_type: CorrectionAction
    intent_vector: List[float]      # [dx, dy, pressure, duration, ...]
    previous_state_hash: Optional[str]  # merkle-like reference to before state
    # ไม่มี user_id, ไม่มี cross-session reference
