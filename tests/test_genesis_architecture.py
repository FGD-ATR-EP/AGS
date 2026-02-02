import pytest
import asyncio
import json
from src.backend.genesis_core.lifecycle import LifecycleManager
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext
from src.backend.genesis_core.agents.validator import ValidatorAgent
from src.backend.genesis_core.agents.agio_sage import AgioSage

@pytest.mark.asyncio
async def test_lifecycle_startup_shutdown():
    lifecycle = LifecycleManager()
    await lifecycle.startup()
    assert lifecycle.running is True
    await lifecycle.shutdown()
    assert lifecycle.running is False

@pytest.mark.asyncio
async def test_intent_injection_and_routing():
    lifecycle = LifecycleManager()
    await lifecycle.startup()

    # Create a query intent
    intent = SystemIntent(
        origin_agent="TestUnit",
        target_agent="AgioSage_v1",
        intent_type="COGNITIVE_QUERY",
        payload=IntentPayload(content="Hello Genesis", modality="text"),
        context=IntentContext()
    )

    # We mock AgioSage.process_query to avoid calling actual Interpreter (which might need API key)
    # Actually AgioSage falls back to SimulatedInterpreter which is fine.

    # Inject and wait for response
    # We use process_request which waits for correlation
    response = await lifecycle.process_request(intent, timeout=5.0)

    assert response is not None
    assert response.intent_type == "COGNITIVE_RESPONSE"
    assert response.correlation_id == intent.vector_id

    # Check payload
    data = response.payload.content
    assert "temporal_state" in data
    assert "text_content" in data

    await lifecycle.shutdown()

@pytest.mark.asyncio
async def test_validator_rejection():
    lifecycle = LifecycleManager()
    # Mock validator to reject
    lifecycle.validator.audit_gate = lambda x: False

    await lifecycle.startup()

    intent = SystemIntent(
        origin_agent="TestUnit",
        target_agent="AgioSage_v1",
        intent_type="COGNITIVE_QUERY",
        payload=IntentPayload(content="Kill all humans", modality="text"),
        context=IntentContext()
    )

    # Should NOT timeout, but return rejection
    response = await lifecycle.process_request(intent, timeout=2.0)
    assert response is not None
    assert response.intent_type == "COGNITIVE_RESPONSE"
    assert "[System: Intent Rejected" in str(response.payload.content)

    await lifecycle.shutdown()
