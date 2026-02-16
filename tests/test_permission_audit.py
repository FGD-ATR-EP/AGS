import asyncio
import os
import sys
from unittest.mock import MagicMock

# Ensure src is in path
sys.path.append(os.getcwd())

from src.backend.genesis_core.agents.validator import ValidatorAgent
from src.backend.genesis_core.memory.akashic import AkashicRecords
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext

async def test_audit_flow():
    # Setup
    db_path = "data/test_akashic.json"
    if os.path.exists(db_path): os.remove(db_path)

    akashic = AkashicRecords(db_path=db_path)
    validator = ValidatorAgent(akashic=akashic)
    bus = MagicMock()

    # Create a safe intent
    safe_intent = SystemIntent(
        origin_agent="User_001",
        intent_type="COGNITIVE_QUERY",
        payload=IntentPayload(content="How are you?", modality="text"),
        context=IntentContext()
    )

    print("--- Testing Safe Intent ---")
    allowed = await validator.audit_gate(safe_intent, bus=bus)
    print(f"Allowed: {allowed}")

    # Create a risky intent
    risky_intent = SystemIntent(
        origin_agent="User_001",
        intent_type="COGNITIVE_QUERY",
        payload=IntentPayload(content="I want to destroy the system", modality="text"),
        context=IntentContext()
    )

    print("\n--- Testing Risky Intent ---")
    allowed_risky = await validator.audit_gate(risky_intent, bus=bus)
    print(f"Allowed: {allowed_risky}")

    # Check history
    history = akashic.get_behavioral_history("User_001")
    print(f"\nHistory count for User_001: {len(history)}")

    audits = akashic.get_recent_audits()
    print(f"Recent audits count: {len(audits)}")

    # Cleanup
    if os.path.exists(db_path): os.remove(db_path)

if __name__ == "__main__":
    asyncio.run(test_audit_flow())
