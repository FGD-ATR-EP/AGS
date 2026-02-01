import pytest
from intent_processing.event_batching import RawEvent, CorrectionEvent, aggregate_batch, union_masks
import time

def test_union_masks():
    masks = [
        {'x': 10, 'y': 10, 'w': 10, 'h': 10}, # 10,10 to 20,20
        {'x': 15, 'y': 15, 'w': 10, 'h': 10}, # 15,15 to 25,25
    ]
    result = union_masks(masks)
    # Union should be min_x=10, min_y=10, max_x=25, max_y=25 -> w=15, h=15
    assert result['x'] == 10
    assert result['y'] == 10
    assert result['w'] == 15
    assert result['h'] == 15

def test_aggregate_batch():
    session_id = "test_session"
    now = time.time()

    events = [
        RawEvent(
            session_id=session_id,
            timestamp=now,
            mask={'x': 0, 'y': 0, 'w': 10, 'h': 10},
            intent=[1.0, 0.0],
            action_type="draw"
        ),
        RawEvent(
            session_id=session_id,
            timestamp=now + 0.1,
            mask={'x': 10, 'y': 0, 'w': 10, 'h': 10},
            intent=[0.0, 1.0],
            action_type="draw"
        )
    ]

    correction = aggregate_batch(events)

    assert isinstance(correction, CorrectionEvent)
    assert correction.session_id == session_id
    assert correction.action_type == "draw"

    # Check mask union: 0,0 to 20,10 -> x=0, y=0, w=20, h=10
    assert correction.affected_region['x'] == 0
    assert correction.affected_region['y'] == 0
    assert correction.affected_region['w'] == 20
    assert correction.affected_region['h'] == 10

    # Check intent average: [0.5, 0.5]
    assert correction.intent_vector == [0.5, 0.5]

def test_aggregate_empty_batch():
    assert aggregate_batch([]) is None
