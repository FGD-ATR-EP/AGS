import unittest
import asyncio
from src.backend.genesis_core.agents.reflector import Reflector, GemOfWisdom

class TestReflector(unittest.TestCase):
    def setUp(self):
        # Mock memory projection
        self.reflector = Reflector(memory_projection=None)

    def test_reflection_failure(self):
        loop = asyncio.get_event_loop()
        gem = loop.run_until_complete(self.reflector.reflect_on_episode("ep-001", success=False))
        self.assertIsNotNone(gem)
        self.assertEqual(gem.title, "Pre-action Validation Needed")
        self.assertEqual(gem.status, "PROPOSED")

    def test_reflection_feedback(self):
        loop = asyncio.get_event_loop()
        gem = loop.run_until_complete(self.reflector.reflect_on_episode("ep-002", success=True, feedback="I prefer shorter summaries"))
        self.assertIsNotNone(gem)
        self.assertIn("User Style Adaptation", gem.title)

    def test_gem_adoption(self):
        gem = GemOfWisdom(
            title="Test Gem",
            context="Test",
            pattern="Pattern",
            principle="Principle",
            confidence=1.0,
            evidence_episodes=["ep-1"]
        )
        self.reflector.adopt_gem(gem)
        active = self.reflector.get_active_gems()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].status, "ACTIVE")

if __name__ == '__main__':
    unittest.main()
