import pytest
import math
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.logenesis import IntentVector, LogenesisState, ExpressionState, IntentPacket

@pytest.fixture
def engine():
    return LogenesisEngine()

def test_entropy_calculation(engine):
    # Test Case 1: Crystal Clear (Low Entropy)
    # High Precision + Low Subjectivity
    clear_vector = IntentVector(
        epistemic_need=0.5, subjective_weight=0.1, decision_urgency=0.1, precision_required=0.9
    )
    assert engine._calculate_entropy(clear_vector) < 0.1

    # Test Case 2: Analytic Hallucination (High Entropy)
    # High Precision + High Subjectivity
    conflicted_vector = IntentVector(
        epistemic_need=0.5, subjective_weight=0.9, decision_urgency=0.1, precision_required=0.9
    )
    entropy = engine._calculate_entropy(conflicted_vector)
    assert entropy > 0.5  # Should be high

    # Test Case 3: Cognitive Gridlock (High Entropy)
    # High Urgency + High Precision
    gridlock_vector = IntentVector(
        epistemic_need=0.5, subjective_weight=0.1, decision_urgency=0.9, precision_required=0.9
    )
    entropy = engine._calculate_entropy(gridlock_vector)
    assert entropy > 0.4 # Should be moderately high

def test_homeostasis_correction(engine):
    # Create a high entropy vector
    high_entropy_vector = IntentVector(
        epistemic_need=0.5, subjective_weight=0.9, decision_urgency=0.1, precision_required=0.9
    )
    initial_entropy = engine._calculate_entropy(high_entropy_vector)
    assert initial_entropy > 0.6

    # Apply Homeostasis
    corrected_vector = engine._apply_homeostasis(high_entropy_vector, initial_entropy)

    # Check if dimensions were clamped
    assert corrected_vector.precision_required < high_entropy_vector.precision_required
    assert corrected_vector.subjective_weight < high_entropy_vector.subjective_weight

    # Check if entropy decreased
    new_entropy = engine._calculate_entropy(corrected_vector)
    assert new_entropy < initial_entropy

def test_temporal_coherence(engine):
    # Initial State
    current_vector = IntentVector(
        epistemic_need=0.1, subjective_weight=0.1, decision_urgency=0.1, precision_required=0.1
    )
    state = ExpressionState(current_vector=current_vector, inertia=0.9) # High Inertia = Low Tolerance

    # Case 1: Fluid Transition (Small Jump)
    small_jump = IntentVector(
        epistemic_need=0.2, subjective_weight=0.2, decision_urgency=0.1, precision_required=0.1
    )
    coherence = engine._calculate_coherence(state, small_jump)
    assert coherence > 0.9

    # Case 2: Disjoint Transition (Massive Jump with High Inertia)
    huge_jump = IntentVector(
        epistemic_need=0.9, subjective_weight=0.9, decision_urgency=0.9, precision_required=0.9
    )
    coherence = engine._calculate_coherence(state, huge_jump)
    assert coherence < 0.5 # Should be penalized

@pytest.mark.asyncio
async def test_state_collapse(engine):
    # Setup rigid previous state
    session_id = "test_collapse"
    engine.state_store._cache[session_id] = ExpressionState(
        current_vector=IntentVector(epistemic_need=0.0, subjective_weight=0.0, decision_urgency=0.0, precision_required=0.0),
        inertia=0.99
    )

    # Create a visual packet that maps to High Urgency (1.0) and High Precision (1.0)
    # This causes High Entropy AND Low Coherence (Jump from 0 to 1)
    packet = IntentPacket(
        modality="visual",
        embedding=None,
        energy_level=1.0,  # Maps to Urgency
        confidence=1.0,    # Maps to Precision
        raw_payload="Mock Visual"
    )

    response = await engine.process(packet, session_id=session_id)

    # Expect Collapse
    assert response.state == LogenesisState.COLLAPSED
    assert response.manifestation_granted is False
    assert response.state_metrics.intent_entropy > 0.8
    assert response.state_metrics.temporal_coherence < 0.2

@pytest.mark.asyncio
async def test_integration_homeostasis_and_feedback(engine):
    # We want to see if `state_metrics` are populated
    packet = IntentPacket(
        modality="text", embedding=None, energy_level=0.5, confidence=1.0, raw_payload="Analyze this securely."
    )

    response = await engine.process(packet, session_id="test_physics")

    assert response.state_metrics is not None
    assert 0.0 <= response.state_metrics.intent_entropy <= 1.0
    assert 0.0 <= response.state_metrics.temporal_coherence <= 1.0
    assert 0.0 <= response.state_metrics.structural_stability <= 1.0
