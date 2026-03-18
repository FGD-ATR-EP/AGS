import unittest
from fastapi.testclient import TestClient
from src.backend.main import app

class TestIntegrationUI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_endpoint(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AG-OS | Notification Center", response.text)
        self.assertIn("System Alerts &amp; Notifications", response.text)

    def test_governance_endpoints(self):
        response = self.client.get("/governance/approvals")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

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
