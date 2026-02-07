import pytest
import asyncio
from src.backend.genesis_core.logenesis.simulated_interpreter import SimulatedIntentInterpreter
from src.backend.genesis_core.models.visual import IntentCategory, BaseShape

@pytest.mark.asyncio
async def test_simulated_interpreter_logic():
    interpreter = SimulatedIntentInterpreter()

    # Case 1: Search Request
    res1 = await interpreter.interpret("search for quantum physics")
    assert res1.intent_category == IntentCategory.REQUEST
    assert "inquiry" in res1.semantic_concepts

    # Case 2: Command / Structure
    res2 = await interpreter.interpret("make a cube structure")
    assert res2.intent_category == IntentCategory.COMMAND
    assert res2.visual_parameters.base_shape == BaseShape.CUBE

    # Case 3: Error / Cracks
    res3 = await interpreter.interpret("system failure critical error")
    assert res3.intent_category == IntentCategory.ERROR
    assert res3.visual_parameters.base_shape == BaseShape.CRACKS
    assert res3.visual_parameters.color_palette == "#FF4500" # OrangeRed hardcoded logic

    # Case 4: Deep Thought / Vortex
    res4 = await interpreter.interpret("analyze deep wisdom spiral")
    assert res4.visual_parameters.base_shape == BaseShape.VORTEX
    assert res4.visual_parameters.color_palette == "#800080"
