import unittest
import os
import json
from src.backend.genesis_core.memory.akashic import AkashicRecords, MemoryProjectionManager

class TestAkashicEnhanced(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/test_akashic_enhanced.json"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.records = AkashicRecords(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_provenance_storage(self):
        payload = {"action": "test_action", "value": 42}
        intent_id = "intent-123"
        causal_link = "intent-000"
        actor = "AgioSage"

        hash_val = self.records.append_record(payload, actor=actor, intent_id=intent_id, causal_link=causal_link)

        self.assertTrue(self.records.verify_hash_chain())

        records = self.records.get_records(limit=1)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['provenance']['actor'], actor)
        self.assertEqual(records[0]['provenance']['intent_id'], intent_id)
        self.assertEqual(records[0]['provenance']['causal_link'], causal_link)
        self.assertEqual(records[0]['payload'], payload)


    def test_verify_hash_chain_detects_prev_hash_tampering(self):
        self.records.append_record({"type": "msg", "text": "first"}, actor="User")
        self.records.append_record({"type": "msg", "text": "second"}, actor="User")

        with open(self.db_path, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data["chain"][1]["prev_hash"] = "f" * 64
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()

        self.assertFalse(self.records.verify_hash_chain())

    def test_projection_episodic(self):
        self.records.append_record({"type": "msg", "text": "hello"}, actor="User")
        self.records.append_record({"type": "thought", "text": "reflecting"}, actor="AgioSage")

        projector = MemoryProjectionManager(self.records)
        timeline = projector.get_episodic_view()

        self.assertEqual(len(timeline), 2)
        self.assertEqual(timeline[0]['who'], "User")
        self.assertEqual(timeline[1]['who'], "AgioSage")
        self.assertEqual(timeline[1]['what'], "thought")

if __name__ == '__main__':
    unittest.main()
