import pytest
import asyncio
from src.backend.genesis_core.models.visual import (
    EmbodimentContract, TemporalState, CognitiveMetadata, IntentData,
    TemporalPhase, ContractIntentCategory, VisualParameters, BaseShape
)
from src.backend.genesis_core.logenesis.embodiment import EmbodimentAdapter
from src.backend.genesis_core.logenesis.simulated_interpreter import SimulatedIntentInterpreter

def test_contract_schema():
    contract = EmbodimentContract(
        temporal_state=TemporalState(phase=TemporalPhase.THINKING, stability=0.5),
        cognitive=CognitiveMetadata(effort=0.8, uncertainty=0.2),
        intent=IntentData(category=ContractIntentCategory.ANALYTIC, purity=1.0)
    )
    assert contract.temporal_state.phase == TemporalPhase.THINKING
    assert contract.cognitive.effort == 0.8

def test_adapter_translation():
    adapter = EmbodimentAdapter()

    # Test 1: Analytic -> Cube
    contract = EmbodimentContract(
        temporal_state=TemporalState(phase=TemporalPhase.MANIFESTING, stability=1.0),
        cognitive=CognitiveMetadata(effort=0.5, uncertainty=0.1),
        intent=IntentData(category=ContractIntentCategory.ANALYTIC, purity=1.0)
    )
    vp = adapter.translate(contract)
    assert vp.visual_parameters.base_shape == BaseShape.CUBE
    assert vp.energy_level == 1.0 - (0.5 * 0.6) # Law 1

    # Test 2: Creative -> Cloud
    contract.intent.category = ContractIntentCategory.CREATIVE
    vp = adapter.translate(contract)
    assert vp.visual_parameters.base_shape == BaseShape.CLOUD

def test_adapter_temporal_override():
    adapter = EmbodimentAdapter()

    # Thinking Phase override
    contract = EmbodimentContract(
        temporal_state=TemporalState(phase=TemporalPhase.THINKING, stability=0.5),
        cognitive=CognitiveMetadata(effort=0.1, uncertainty=0.1), # Low effort shouldn't matter if thinking
        intent=IntentData(category=ContractIntentCategory.CHIT_CHAT, purity=1.0)
    )
    vp = adapter.translate(contract)
    # Expect Thinking Visuals (Vortex, High Energy)
    assert vp.visual_parameters.base_shape == BaseShape.VORTEX
    assert vp.energy_level > 0.8
    assert vp.visual_parameters.turbulence > 0.5

@pytest.mark.asyncio
async def test_simulated_interpreter():
    interpreter = SimulatedIntentInterpreter()

    # Test "analyze" keyword -> Analytic
    contract = await interpreter.interpret("Please analyze this data")
    assert contract.intent.category == ContractIntentCategory.ANALYTIC
    assert contract.cognitive.effort >= 0.8

    # Test "story" keyword -> Creative
    contract = await interpreter.interpret("Tell me a story")
    assert contract.intent.category == ContractIntentCategory.CREATIVE
