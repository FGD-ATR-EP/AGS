import sys
import os
import pytest
from dataclasses import FrozenInstanceError

# Add project root to sys.path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.backend.genesis_core.logenesis.correction_schemas import CorrectionAction, SpatialMask, CorrectionEvent, StructuralGuide

def test_correction_action_enum():
    assert CorrectionAction.MOVE.value == "move"
    assert CorrectionAction.ERASE.value == "erase"
    assert CorrectionAction.REDRAW.value == "redraw"
    assert CorrectionAction.EMPHASIZE.value == "emphasize"
    assert CorrectionAction.LOCK.value == "lock"

def test_structural_guide_enum():
    assert StructuralGuide.TILE.value == "tile"
    assert StructuralGuide.EDGE.value == "canny"
    assert StructuralGuide.DEPTH.value == "depth"

def test_spatial_mask_creation():
    mask = SpatialMask(x_min=0, y_min=0, x_max=10, y_max=10)
    assert mask.x_min == 0
    assert mask.y_max == 10
    assert isinstance(mask.x_min, int)

def test_spatial_mask_immutability():
    mask = SpatialMask(x_min=0, y_min=0, x_max=10, y_max=10)
    with pytest.raises(FrozenInstanceError):
        mask.x_min = 5

def test_correction_event_creation():
    mask = SpatialMask(x_min=0, y_min=0, x_max=10, y_max=10)
    event = CorrectionEvent(
        event_id="test-uuid",
        session_id="session-123",
        timestamp=1234567890.0,
        affected_region=mask,
        action_type=CorrectionAction.MOVE,
        intent_vector=[1.0, 2.0, 0.5, 100.0],
        mode="persistent"
    )

    assert event.event_id == "test-uuid"
    assert event.action_type == CorrectionAction.MOVE
    assert event.affected_region.x_min == 0
    assert event.intent_vector == [1.0, 2.0, 0.5, 100.0]
    assert event.mode == "persistent"

def test_correction_event_default_mode():
    mask = SpatialMask(x_min=0, y_min=0, x_max=10, y_max=10)
    event = CorrectionEvent(
        event_id="test-uuid",
        session_id="session-123",
        timestamp=1234567890.0,
        affected_region=mask,
        action_type=CorrectionAction.MOVE,
        intent_vector=[1.0, 2.0, 0.5]
    )
    assert event.mode == "short_decay"
