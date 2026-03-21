from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.genesis_core.protocol.abe_contract import ABEContract
import json
import time

def test_aetherium_flow_secured():
    # Trigger Startup Events
    with TestClient(app) as client:
        # 1. Generate Contract
        contract = ABEContract.create_new("TestEntity", "OBSERVER")
        contract_json = json.loads(contract.to_json())

        # 2. Mock Internal Key Generation (Bypassing Overseer UI for Test)
        # Note: In a real test we might hit an internal API or mock KeyManager.
        # But we can access app.state if we were using an async client in-process.
        # Since TestClient is sync, we can't easily access app.state of the running app unless we use the same instance?
        # TestClient creates its own lifespan.

        # We need a valid key. The KeyManager initializes with no keys.
        # However, we can use the "Internal" backdoor if we implement one, OR
        # we can just test the Rejection first.

        # TEST REJECTION (No Key)
        response = client.post("/v1/session", json={
            "abe_contract": contract_json
        })
        assert response.status_code == 400 # Missing Key

        # TEST REJECTION (Invalid Key)
        response = client.post("/v1/session", json={
            "abe_contract": contract_json,
            "access_key": "invalid-key"
        })
        assert response.status_code == 403 # Access Denied
