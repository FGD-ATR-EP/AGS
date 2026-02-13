import pytest
import os
import json
from src.backend.genesis_core.logenesis.engine import LogenesisEngine, StateStore
from src.backend.genesis_core.models.logenesis import IntentVector, ExpressionState

@pytest.fixture
def clean_state_store():
    filename = "test_logenesis_state.json"
    if os.path.exists(filename):
        os.remove(filename)
    yield filename
    if os.path.exists(filename):
        os.remove(filename)

@pytest.mark.asyncio
async def test_drift_mechanics(clean_state_store):
    engine = LogenesisEngine()
    engine.state_store = StateStore(filepath=clean_state_store)
    session_id = "test_session_1"

    # 1. Initial State (Neutral)
    state_0 = engine.state_store.get_state(session_id)
    assert state_0.current_vector.epistemic_need == 0.1
    assert state_0.current_vector.decision_urgency == 0.1

    # 2. Apply "Business/Urgent" input
    # "urgent" keyword triggers decision_urgency=0.9
    response_1 = await engine.process("This is urgent action required.", session_id=session_id)

    state_1 = engine.state_store.get_state(session_id)
    # Urgency should be high in input (0.9), so inertia drops.
    # Current (0.1) -> Target (0.9).
    # Since urgency is high, effective inertia is low (~0.18).
    # New value should be significantly closer to 0.9.

    assert state_1.current_vector.decision_urgency > 0.5
    assert state_1.current_vector.decision_urgency < 0.95 # Shouldn't be perfect 1.0 instantly unless inertia is 0

    print(f"Drift Step 1: Urgency moved from 0.1 to {state_1.current_vector.decision_urgency}")

    # 3. Apply "Casual/Subjective" input
    # "feel" keyword triggers subjective_weight=0.9
    response_2 = await engine.process("I feel we need to take it slow.", session_id=session_id)

    state_2 = engine.state_store.get_state(session_id)

    # Subjective weight should rise, but because urgency was low in this input, inertia is higher (slower change).
    assert state_2.current_vector.subjective_weight > 0.1
    print(f"Drift Step 2: Subjective moved from 0.1 to {state_2.current_vector.subjective_weight}")

@pytest.mark.asyncio
async def test_persistence(clean_state_store):
    # Phase 1: Engine A
    engine_a = LogenesisEngine()
    engine_a.state_store = StateStore(filepath=clean_state_store)
    session_id = "persist_session"

    await engine_a.process("urgent", session_id=session_id)
    state_a = engine_a.state_store.get_state(session_id)

    # Phase 2: Engine B (Simulate server restart)
    # Should load from the same file
    engine_b = LogenesisEngine()
    engine_b.state_store = StateStore(filepath=clean_state_store)
    state_b = engine_b.state_store.get_state(session_id)

    assert state_b.current_vector.decision_urgency == state_a.current_vector.decision_urgency
    assert state_b.last_updated == state_a.last_updated

@pytest.mark.asyncio
async def test_response_tone_adaptation(clean_state_store):
    engine = LogenesisEngine()
    engine.state_store = StateStore(filepath=clean_state_store)
    session_id = "tone_session"

    # Force state to High Precision
    state = engine.state_store.get_state(session_id)
    state.current_vector.precision_required = 0.9
    state.current_vector.epistemic_need = 0.8
    engine.state_store.update_state(session_id, state)

    # Query
    response = await engine.process("What is the status?", session_id=session_id)

    # Expect formal language
    assert "alignment" in response.text_content or "Structure" in response.text_content
    # assert "System nominal" not in response.text_content # Should choose the precision path
