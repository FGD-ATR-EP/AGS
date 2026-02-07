import pytest
import asyncio
from unittest.mock import patch, MagicMock
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.logenesis import LogenesisResponse, IntentVector, ExpressionState

@pytest.mark.asyncio
async def test_reasoned_response_subjective():
    # Patch _drift_state to bypass inertia and return input intent directly
    with patch.object(LogenesisEngine, '_drift_state') as mock_drift:
        engine = LogenesisEngine()

        target_vector = IntentVector(
            epistemic_need=0.4,
            subjective_weight=0.9,
            decision_urgency=0.1,
            precision_required=0.1
        )
        mock_drift.return_value = ExpressionState(
            current_vector=target_vector,
            velocity=1.0, # High velocity to bypass noise filter
            inertia=0.0
        )

        # Input that should trigger subjective weight
        response = await engine.process("I am worried about the market risk")

        assert isinstance(response, LogenesisResponse)
        # Verify the drift pushed the state towards subjective
        assert response.intent_debug.subjective_weight > 0.7

@pytest.mark.asyncio
async def test_reasoned_response_epistemic():
    with patch.object(LogenesisEngine, '_drift_state') as mock_drift:
        engine = LogenesisEngine()

        target_vector = IntentVector(
            epistemic_need=0.8,
            subjective_weight=0.1,
            decision_urgency=0.1,
            precision_required=0.95
        )
        mock_drift.return_value = ExpressionState(
            current_vector=target_vector,
            velocity=1.0, # Bypass noise filter
            inertia=0.0
        )

        response = await engine.process("Analyze the structure of this code")

        assert response.intent_debug.epistemic_need > 0.6

@pytest.mark.asyncio
async def test_nirodha_audio():
    engine = LogenesisEngine()
    response = await engine.process("Rest now, enough")
    assert response.state.name == "NIRODHA"
