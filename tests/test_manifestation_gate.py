import pytest
from unittest.mock import MagicMock, AsyncMock
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.light import LightAction
from src.backend.genesis_core.models.logenesis import IntentPacket
from src.backend.genesis_core.models.visual import VisualParameters, IntentCategory, BaseShape, VisualSpecifics

# --- Fixtures ---
@pytest.fixture
def engine():
    eng = LogenesisEngine()
    # Bypass physics coherence checks for these tests to focus on the gate logic
    eng._calculate_coherence = MagicMock(return_value=1.0)
    return eng

# --- Tests ---

@pytest.mark.asyncio
async def test_explicit_command_bypass(engine):
    """
    Verify that explicit commands trigger manifestation regardless of energy.
    """
    # Mock Lifecycle Response
    mock_response_intent = MagicMock()
    mock_response_intent.intent_type = "COGNITIVE_RESPONSE"
    mock_response_intent.payload.content = {
        "text_content": "Executing command.",
        "temporal_state": {"phase": "MANIFESTING", "stability": 1.0},
        "cognitive": {"effort": 0.1, "uncertainty": 0.0},
        "intent": {"category": "SYSTEM_OPS", "purity": 1.0}
    }
    engine.lifecycle.process_request = AsyncMock(return_value=mock_response_intent)

    # Mock Adapter to return VisualParams for a Command
    engine.adapter.translate = MagicMock(return_value=VisualParameters(
        intent_category=IntentCategory.COMMAND,
        emotional_valence=0.0,
        energy_level=0.1, # Even low energy should pass for commands
        semantic_concepts=["circle"],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.CIRCLE,
            turbulence=0.0,
            particle_density=1.0,
            color_palette="#FFFFFF"
        )
    ))

    response = await engine.process("Make a circle")

    assert response.manifestation_granted is True
    assert response.light_intent is not None
    assert response.light_intent.shape_name == "circle"

@pytest.mark.asyncio
async def test_neutral_conversation_blocked(engine):
    """
    Verify that low-intensity conversation does NOT trigger manifestation.
    """
    # Mock Lifecycle Response
    mock_response_intent = MagicMock()
    mock_response_intent.intent_type = "COGNITIVE_RESPONSE"
    mock_response_intent.payload.content = {
        "text_content": "Just chatting.",
        "temporal_state": {"phase": "LISTENING", "stability": 1.0},
        "cognitive": {"effort": 0.1, "uncertainty": 0.0},
        "intent": {"category": "CHIT_CHAT", "purity": 1.0}
    }
    engine.lifecycle.process_request = AsyncMock(return_value=mock_response_intent)

    # Mock Adapter to return Low Energy CHAT
    engine.adapter.translate = MagicMock(return_value=VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.1,
        energy_level=0.1, # Too low to manifest
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(base_shape=BaseShape.CLOUD, turbulence=0.1, particle_density=0.1, color_palette="#FFFFFF")
    ))

    response = await engine.process("Hello, how are you?")

    # Should be False because energy/valence/turbulence are all low
    assert response.manifestation_granted is False
    assert response.light_intent is None

@pytest.mark.asyncio
async def test_high_intensity_manifestation(engine):
    """
    Verify that HIGH intensity conversation triggers manifestation.
    """
    # Mock Lifecycle Response
    mock_response_intent = MagicMock()
    mock_response_intent.intent_type = "COGNITIVE_RESPONSE"
    mock_response_intent.payload.content = {
        "text_content": "I am angry!",
        "temporal_state": {"phase": "MANIFESTING", "stability": 1.0},
        "cognitive": {"effort": 0.8, "uncertainty": 0.0},
        "intent": {"category": "CREATIVE", "purity": 1.0}
    }
    engine.lifecycle.process_request = AsyncMock(return_value=mock_response_intent)

    # Mock Adapter to return High Energy CHAT
    engine.adapter.translate = MagicMock(return_value=VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.0,
        energy_level=0.8, # > 0.6 Threshold
        semantic_concepts=[],
        visual_parameters=VisualSpecifics(base_shape=BaseShape.VORTEX, turbulence=0.8, particle_density=0.8, color_palette="#FF0000")
    ))

    response = await engine.process("I feel intense emotion!")

    assert response.manifestation_granted is True
    assert response.light_intent is not None
    assert response.light_intent.shape_name == "vortex"

@pytest.mark.asyncio
async def test_manifestation_gate_precision(engine):
    """
    Verify that High Precision (Analysis) triggers manifestation.
    Logic: If intent is CHAT but implies deep analysis (high density/energy), it might manifest.
    But strictly, LogenesisEngine._check_manifestation_gate checks energy, valence, turbulence.
    """
    # Mock Lifecycle Response
    mock_response_intent = MagicMock()
    mock_response_intent.intent_type = "COGNITIVE_RESPONSE"
    mock_response_intent.payload.content = {
        "text_content": "Analyzing data.",
        "temporal_state": {"phase": "THINKING", "stability": 1.0},
        "cognitive": {"effort": 0.8, "uncertainty": 0.0},
        "intent": {"category": "ANALYTIC", "purity": 1.0}
    }
    engine.lifecycle.process_request = AsyncMock(return_value=mock_response_intent)

    # Mock Adapter for Analysis
    engine.adapter.translate = MagicMock(return_value=VisualParameters(
        intent_category=IntentCategory.CHAT,
        emotional_valence=0.0,
        energy_level=0.5,
        semantic_concepts=["analysis"],
        visual_parameters=VisualSpecifics(
            base_shape=BaseShape.CUBE,
            turbulence=0.7, # High turbulence/complexity triggers gate
            particle_density=0.9,
            color_palette="#0000FF"
        )
    ))

    response = await engine.process("Analyze the code.")

    # Triggered by turbulence > 0.6
    assert response.manifestation_granted is True
    assert response.light_intent is not None
    assert response.light_intent.shape_name == "cube"
