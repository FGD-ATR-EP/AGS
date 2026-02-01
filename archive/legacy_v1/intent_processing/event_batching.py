import time
from uuid import uuid4
from dataclasses import dataclass
from typing import List, Dict, Any, Union
import numpy as np

@dataclass
class RawEvent:
    session_id: str
    timestamp: float
    mask: Dict[str, float]  # {'x':, 'y':, 'w':, 'h':}
    intent: List[float]
    action_type: str

@dataclass
class CorrectionEvent:
    event_id: str
    session_id: str
    timestamp: float
    affected_region: Dict[str, float]
    action_type: str
    intent_vector: List[float]
    mode: str

def union_masks(masks: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Computes the bounding box union of multiple masks.
    Assumes mask format: {'x': x, 'y': y, 'w': width, 'h': height}
    """
    if not masks:
        return {'x': 0, 'y': 0, 'w': 0, 'h': 0}

    min_x = min(m['x'] for m in masks)
    min_y = min(m['y'] for m in masks)
    max_x = max(m['x'] + m['w'] for m in masks)
    max_y = max(m['y'] + m['h'] for m in masks)

    return {
        'x': min_x,
        'y': min_y,
        'w': max_x - min_x,
        'h': max_y - min_y
    }

def average_intent(intents: List[List[float]]) -> List[float]:
    """
    Computes the average vector of intents.
    """
    if not intents:
        return []

    # Convert to numpy array for easy averaging
    arr = np.array(intents)
    return np.mean(arr, axis=0).tolist()

def aggregate_batch(events: List[RawEvent]) -> CorrectionEvent:
    """
    Aggregates a batch of RawEvents into a single CorrectionEvent.
    """
    if not events:
        return None

    mask = union_masks([e.mask for e in events])
    intent = average_intent([e.intent for e in events])

    return CorrectionEvent(
        event_id=str(uuid4()),
        session_id=events[0].session_id,
        timestamp=time.time(),
        affected_region=mask,
        action_type=events[-1].action_type,
        intent_vector=intent,
        mode="short_decay"
    )
