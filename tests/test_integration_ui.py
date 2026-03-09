import unittest
from fastapi.testclient import TestClient
from src.backend.main import app

class TestIntegrationUI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_dashboard_endpoint(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn("AETHERIUM SYNDICATE INSPECTRA", response.text)

    def test_governance_endpoints(self):
        response = self.client.get("/governance/approvals")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == '__main__':
    unittest.main()
