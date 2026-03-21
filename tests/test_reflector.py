import unittest
import asyncio

from src.backend.genesis_core.agents.reflector import Reflector, GemStatus


class TestReflector(unittest.TestCase):
    def setUp(self):
        self.reflector = Reflector(memory_projection=None)

    def test_reflection_failure(self):
        gem = asyncio.run(self.reflector.reflect_on_episode("ep-001", success=False))
        self.assertIsNotNone(gem)
        self.assertEqual(gem.title, "Pre-action Validation Needed")
        self.assertEqual(gem.status, GemStatus.PROPOSED)

    def test_reflection_feedback(self):
        gem = asyncio.run(
            self.reflector.reflect_on_episode("ep-002", success=True, feedback="I prefer shorter summaries")
        )
        self.assertIsNotNone(gem)
        self.assertIn("User Style Adaptation", gem.title)

    def test_replay_episode(self):
        asyncio.run(self.reflector.reflect_on_episode("ep-003", success=False))
        replayed = asyncio.run(self.reflector.replay_episode("ep-003"))
        self.assertIsNotNone(replayed)
        self.assertIn("replay", replayed.evidence_episodes[0])


if __name__ == '__main__':
    unittest.main()
