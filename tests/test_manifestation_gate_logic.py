import pytest
from unittest.mock import AsyncMock, MagicMock
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.visual import VisualParameters, IntentCategory, BaseShape, VisualSpecifics

def setup_engine():
    engine = LogenesisEngine()
    # Bypass physics
    engine._calculate_coherence = MagicMock(return_value=1.0)
    # Mock Lifecycle (generic valid response)
    mock_resp = MagicMock()
    mock_resp.intent_type = "COGNITIVE_RESPONSE"
    mock_resp.payload.content = {
        "text_content": "Response",
        "temporal_state": {"phase": "MANIFESTING", "stability": 1.0},
        "cognitive": {"effort": 0.5, "uncertainty": 0.0},
        "intent": {"category": "CHIT_CHAT", "purity": 1.0}
    }
    engine.lifecycle.process_request = AsyncMock(return_value=mock_resp)
    return engine

@pytest.mark.asyncio
async def test_manifestation_gate_command():
    engine = setup_engine()

    vp = VisualParameters(
        intent_category=IntentCategory.COMMAND,
        emotional_valence=0.0,
        energy_level=0.5,
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.SPHERE,
            turbulence=0.0,
            particle_density=0.5,
            color_palette="#FFFFFF"
        )
    )
    engine.adapter.translate = MagicMock(return_value=vp)

    response = await engine.process("command")
    assert response.manifestation_granted is True
    assert response.light_intent is not None

@pytest.mark.asyncio
async def test_manifestation_gate_chat_low_energy():
    engine = setup_engine()

    vp = VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.1, # Low
        energy_level=0.1, # Low
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.SPHERE,
            turbulence=0.1, # Low
            particle_density=0.5,
            color_palette="#FFFFFF"
        )
    )
    engine.adapter.translate = MagicMock(return_value=vp)

    response = await engine.process("chat")
    assert response.manifestation_granted is False
    assert response.light_intent is None

@pytest.mark.asyncio
async def test_manifestation_gate_chat_high_energy():
    engine = setup_engine()

    vp = VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.1,
        energy_level=0.8, # High -> Trigger
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.SPHERE,
            turbulence=0.1,
            particle_density=0.5,
            color_palette="#FFFFFF"
        )
    )
    engine.adapter.translate = MagicMock(return_value=vp)

    response = await engine.process("chat")
    assert response.manifestation_granted is True
    assert response.light_intent is not None

@pytest.mark.asyncio
async def test_manifestation_gate_chat_high_emotion():
    engine = setup_engine()

    vp = VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.9, # High -> Trigger
        energy_level=0.1,
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.SPHERE,
            turbulence=0.1,
            particle_density=0.5,
            color_palette="#FFFFFF"
        )
    )
    engine.adapter.translate = MagicMock(return_value=vp)

    response = await engine.process("chat")
    assert response.manifestation_granted is True

@pytest.mark.asyncio
async def test_manifestation_gate_chat_high_turbulence():
    engine = setup_engine()

    vp = VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.1,
        energy_level=0.1,
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.SPHERE,
            turbulence=0.9, # High -> Trigger
            particle_density=0.5,
            color_palette="#FFFFFF"
        )
    )
    engine.adapter.translate = MagicMock(return_value=vp)

    response = await engine.process("chat")
    assert response.manifestation_granted is True
