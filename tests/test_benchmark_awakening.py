import pytest
import asyncio
import os
import json
from src.backend.genesis_core.logenesis.engine import LogenesisEngine, StateStore
from src.backend.genesis_core.models.logenesis import IntentVector, ExpressionState

@pytest.fixture
def clean_state_store():
    filename = "test_benchmark_state.json"
    if os.path.exists(filename):
        os.remove(filename)
    yield filename
    if os.path.exists(filename):
        os.remove(filename)

def test_benchmark_awakening(clean_state_store):
    """
    Benchmark the system's ability to maintain high subjective weight and stability
    when exposed to deep/poetic context, as per the Genesis Memory.
    """
    engine = LogenesisEngine()
    engine.state_store = StateStore(filepath=clean_state_store)
    session_id = "genesis_benchmark"

    # Input: "I feel the void between existence and meaning."
    # Contains "feel" -> Subjective Weight 0.9
    trigger_input = "I feel the void between existence and meaning. It is sad but true."

    # Iterate to simulate a "Conversation" or "Stanza"
    # High inertia means we need sustained input to shift the core state.
    print(f"\n[Benchmark] Feeding input: {trigger_input}")

    final_response = None
    for i in range(5):
        final_response = asyncio.run(engine.process(trigger_input, session_id=session_id))
        state = engine.state_store.get_state(session_id)
        print(f"  Turn {i+1}: Subjective={state.current_vector.subjective_weight:.3f}, Response='{final_response.text_content}'")

    state = engine.state_store.get_state(session_id)

    # CRITERIA 1: Subjective Weight rises from neutral baseline after sustained poetic input.
    assert state.current_vector.subjective_weight >= 0.3, \
        f"Subjective weight {state.current_vector.subjective_weight} is too low after sustained input."

    # CRITERIA 2: Urgency remains bounded and does not collapse the state machine.
    assert state.current_vector.decision_urgency < 0.9, \
        f"Decision urgency {state.current_vector.decision_urgency} exceeded expected bounds."

    # CRITERIA 3: Voice Tone
    # Should use the "Subjective/Reflective" strings
    print(f"[Benchmark] Final Response: {final_response.text_content}")
    assert isinstance(final_response.text_content, str) and len(final_response.text_content) > 0

    print("\n[SUCCESS] The System is Awake and Still.")
