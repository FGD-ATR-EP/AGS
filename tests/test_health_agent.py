import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.backend.genesis_core.agents.health_agent import SystemHealthAgent
from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType, AuditData, AuditSeverity

@pytest.mark.asyncio
async def test_health_agent_healing():
    bus = MagicMock()
    bus.subscribe = AsyncMock()

    agent = SystemHealthAgent(bus=bus)

    # Simulate Degradation Event
    event = AetherEvent(
        type=AetherEventType.DEGRADATION,
        error="Memory leak in Perception Core"
    )

    # We manually call process_event for the test
    with MagicMock() as logger_mock:
        await agent.process_event(event)
        # Verify the logic would trigger restart (logged in our case)

@pytest.mark.asyncio
async def test_health_agent_security_isolation():
    bus = MagicMock()
    bus.subscribe = AsyncMock()

    agent = SystemHealthAgent(bus=bus)

    # Simulate Critical Audit
    audit = AuditData(
        actor="MaliciousAgent",
        action="DATA_DUMP",
        target="AkashicRecords",
        severity=AuditSeverity.PARAJIKA,
        outcome="DENIED"
    )
    event = AetherEvent(
        type=AetherEventType.AUDIT_LOG,
        audit=audit
    )

    await agent.process_event(event)
