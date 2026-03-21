import os
import tempfile
import unittest
import uuid

from src.backend.genesis_core.agents.reflector import Reflector, PolicyUpdater, GemStatus
from src.backend.genesis_core.agents.validator import ValidatorAgent
from src.backend.genesis_core.governance.core import GovernanceCore
from src.backend.genesis_core.memory.akashic import AkashicRecords, MemoryProjectionManager
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext


class TestEndToEndGovernanceGemFlow(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "akashic.json")
        self.gem_path = os.path.join(self.temp_dir.name, "derived_gems.json")

        self.ledger = AkashicRecords(db_path=self.db_path)
        self.projection = MemoryProjectionManager(self.ledger)
        self.projection.gem_store_path = self.gem_path
        self.gov = GovernanceCore(config={"auto_approve_tier_1": False}, ledger=self.ledger)
        self.validator = ValidatorAgent(governance=self.gov)
        self.reflector = Reflector(memory_projection=self.projection)
        self.policy_updater = PolicyUpdater(memory_projection=self.projection)

    async def asyncTearDown(self):
        self.temp_dir.cleanup()

    async def test_intent_to_gem_flow(self):
        intent = SystemIntent(
            origin_agent="AgioSage",
            intent_type="EXECUTION_REQUEST",
            payload=IntentPayload(content={"action": "send_email", "to": "ops@example.com"}, modality="json"),
            context=IntentContext(),
        )

        allowed = self.validator.audit_gate(intent)
        self.assertFalse(allowed)  # governance gate
        self.assertEqual(len(self.gov.pending_approvals), 1)

        request = list(self.gov.pending_approvals.values())[0]
        self.assertIn("action", request.preview_data)  # preview exists

        approved = self.gov.handle_approval(request.request_id, "APPROVED")
        self.assertTrue(approved)

        gem = await self.reflector.reflect_on_episode(
            episode_id=f"ep-{uuid.uuid4().hex[:8]}",
            success=False,
            feedback=None,
            metadata={"intent_id": intent.vector_id, "request_id": request.request_id},
        )
        self.assertIsNotNone(gem)
        self.assertEqual(gem.status, GemStatus.PROPOSED)

        self.policy_updater.approve_gem(gem, approver="human_overseer", source_episode=request.request_id)
        self.policy_updater.activate_gem(gem, actor="policy_engine", source_episode=request.request_id)

        self.assertEqual(gem.status, GemStatus.ACTIVE)

        chain = self.ledger.get_records(limit=20)
        event_types = [b.get("payload", {}).get("type") for b in chain]
        self.assertIn("approval_requested", event_types)
        self.assertIn("approval_decided", event_types)
        self.assertIn("gem_approved", event_types)
        self.assertIn("gem_activated", event_types)

        gem_projection = self.projection.get_gem_projection()
        self.assertIn(gem.gem_id, gem_projection["gems"])
        self.assertEqual(gem_projection["gems"][gem.gem_id]["current"]["status"], GemStatus.ACTIVE)

    async def test_shadow_mode_policy_simulation(self):
        sample_gem = {"gem_id": "g-1", "title": "Preview First", "principle": "Always preview"}
        result = self.gov.simulate_rule_promotion(sample_gem, shadow_mode=True)
        self.assertEqual(result["mode"], "shadow")
        self.assertEqual(result["promoted_rule"]["status"], "SHADOW")


if __name__ == "__main__":
    unittest.main()
