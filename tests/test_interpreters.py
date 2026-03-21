import pytest
import asyncio
from src.backend.genesis_core.logenesis.simulated_interpreter import SimulatedIntentInterpreter
from src.backend.genesis_core.models.visual import ContractIntentCategory

@pytest.mark.asyncio
async def test_simulated_interpreter_logic():
    interpreter = SimulatedIntentInterpreter()

    # Case 1: Search Request
    res1 = await interpreter.interpret("search for quantum physics")
    assert res1.intent.category == ContractIntentCategory.ANALYTIC
    assert "analyz" in res1.text_content.lower()

    # Case 2: Command / Structure
    res2 = await interpreter.interpret("system status")
    assert res2.intent.category == ContractIntentCategory.SYSTEM_OPS
    assert "system" in res2.text_content.lower()

    # Case 3: Creative prompt
    res3 = await interpreter.interpret("create a short poem")
    assert res3.intent.category == ContractIntentCategory.CREATIVE
    assert "imagining" in res3.text_content.lower()

    # Case 4: Nuance modifiers
    res4 = await interpreter.interpret("analyze complex system maybe")
    assert res4.cognitive.effort == 1.0
    assert res4.cognitive.uncertainty == 0.8
