import unittest

from src.backend.genesis_core.governance.scenario_presets import (
    get_scenario_preset,
    list_scenario_presets,
)


class TestGovernanceScenarioPresets(unittest.TestCase):
    def test_list_contains_expected_shape(self):
        presets = list_scenario_presets()
        self.assertGreaterEqual(len(presets), 1)
        first = presets[0]
        self.assertIn("preset_id", first)
        self.assertIn("action_count", first)

    def test_get_unknown_preset_raises(self):
        with self.assertRaises(KeyError):
            get_scenario_preset("unknown")


if __name__ == "__main__":
    unittest.main()
