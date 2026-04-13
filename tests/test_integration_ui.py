import unittest
from fastapi.testclient import TestClient
from src.backend.main import app

from src.backend.routers.governance import lifecycle
from src.backend.genesis_core.governance.core import ApprovalRequest, ActionTier

class TestIntegrationUI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_dashboard_endpoint(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AG-OS | Notification Center", response.text)
        self.assertIn("System Alerts &amp; Notifications", response.text)

    def test_governance_endpoints(self):
        response = self.client.get("/governance/approvals")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_governance_decide_rejected_is_successful_outcome(self):
        request_id = "req-integration-reject"
        lifecycle.validator.governance.pending_approvals[request_id] = ApprovalRequest(
            request_id=request_id,
            tier=ActionTier.TIER_2_EXTERNAL_IMPACT,
            actor="integration-test",
            intent_id="intent-integration-reject",
            action_type="send_email",
            preview_data={"recipient": "ops@example.com"},
        )

        response = self.client.post("/governance/decide", json={"request_id": request_id, "decision": "rejected"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        self.assertEqual(response.json()["outcome"], "REJECTED")

    def test_governance_decide_unknown_request_returns_404(self):
        response = self.client.post("/governance/decide", json={"request_id": "req-does-not-exist", "decision": "APPROVED"})
        self.assertEqual(response.status_code, 404)

    def test_governance_scenario_presets_endpoints(self):
        response = self.client.get("/governance/scenario-presets")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("presets", payload)
        self.assertGreaterEqual(len(payload["presets"]), 1)

        preset_id = payload["presets"][0]["preset_id"]
        run_response = self.client.post("/governance/scenario-presets/run", json={"preset_id": preset_id})
        self.assertEqual(run_response.status_code, 200)
        run_payload = run_response.json()
        self.assertEqual(run_payload["preset_id"], preset_id)
        self.assertIn("summary", run_payload)

    def test_governance_scenario_run_unknown_preset(self):
        response = self.client.post("/governance/scenario-presets/run", json={"preset_id": "unknown"})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
