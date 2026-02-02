import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import logging

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging to capture output during tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestVisionCoreHeadless(unittest.TestCase):
    def setUp(self):
        # We need to remove the module from sys.modules if it exists
        # so that it gets re-imported with our patches active.
        self.module_name = "src.backend.departments.design.chromatic.aetherium_vision_core"
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]

        # Also remove torch if it's there, to be safe, though we will patch usage of it.
        # Actually, the cleanest way to trigger the ImportError in the module
        # is to patch sys.modules so 'torch' appears missing.

    def tearDown(self):
        # Clean up by removing the module again so subsequent tests
        # (if running in same process) re-import normally.
        if self.module_name in sys.modules:
            del sys.modules[self.module_name]

    def test_headless_execution(self):
        """
        Verify that AetheriumVisionCore functions correctly when torch is missing.
        This forces the use of MockModule, MockNN, MockTorch, etc.
        """
        with patch.dict(sys.modules, {'torch': None}):
            # Attempt import. This should trigger the ImportError clause.
            try:
                from src.backend.departments.design.chromatic.aetherium_vision_core import (
                    AetheriumVisionCore, AetherOutput, AetherState, TORCH_AVAILABLE
                )
            except ImportError as e:
                self.fail(f"Failed to import module in headless mode: {e}")

            # Verify we are in headless mode
            self.assertFalse(TORCH_AVAILABLE, "TORCH_AVAILABLE should be False in headless test")

            # Instantiate Core
            core = AetheriumVisionCore()

            # Create dummy input (numpy array since torch is 'missing')
            import numpy as np
            dummy_input = np.random.rand(1, 3, 224, 224).astype(np.float32)

            # Run forward pass
            # This triggers the MockModule.__call__ -> forward logic
            output = core(dummy_input)

            # Assertions
            self.assertIsInstance(output, AetherOutput)

            # Logic check:
            # MockModule.load_estimator.forward returns 0.5 (default in code)
            # Code:
            # if load < 0.2: STABILIZED
            # elif load < 0.5: PERCEPTION
            # else: ANALYSIS
            # So 0.5 results in ANALYSIS.

            self.assertEqual(output.state, AetherState.ANALYSIS)
            self.assertEqual(output.energy_level, 0.5)
            self.assertEqual(output.confidence, 0.5)

            # Check that embedding is a mock object/array
            # In CorticalReasoningLayer.forward: return torch.randn(...) -> np.zeros(...)
            self.assertTrue(hasattr(output.embedding, 'shape'))

if __name__ == '__main__':
    unittest.main()
