import unittest
import os
import shutil
import asyncio
from src.backend.genesis_core.vessels.workspace import WorkspaceVessel
from src.backend.genesis_core.governance.core import ActionTier

class TestWorkspaceVessel(unittest.TestCase):
    def setUp(self):
        self.test_root = "test_workspace"
        self.vessel = WorkspaceVessel(workspace_root=self.test_root)

    def tearDown(self):
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

    def test_safe_path(self):
        # Should allow
        self.vessel._safe_path("docs/plan.md")
        # Should block
        with self.assertRaises(PermissionError):
            self.vessel._safe_path("../secret.txt")

    def test_simulate(self):
        loop = asyncio.get_event_loop()
        preview = loop.run_until_complete(self.vessel.simulate("write_file", {"path": "test.txt", "content": "Hello"}))
        self.assertEqual(preview.risk_tier, ActionTier.TIER_1_REVERSIBLE_LOW_RISK)
        self.assertIn("Create file", preview.summary)

    def test_execute_write_read(self):
        loop = asyncio.get_event_loop()
        # Write
        loop.run_until_complete(self.vessel.execute("write_file", {"path": "hi.txt", "content": "Aether"}))
        # Read
        result = loop.run_until_complete(self.vessel.execute("read_file", {"path": "hi.txt"}))
        self.assertEqual(result["content"], "Aether")

if __name__ == '__main__':
    unittest.main()
