import sys
from unittest.mock import MagicMock

# Helper to mock modules
def mock_module(module_name):
    if module_name not in sys.modules:
        m = MagicMock()
        sys.modules[module_name] = m
        # Recursively mock sub-packages if needed (simple approximation)
        parts = module_name.split(".")
        if len(parts) > 1:
            parent = sys.modules.get(parts[0])
            if not parent:
                parent = MagicMock()
                sys.modules[parts[0]] = parent
            setattr(parent, parts[1], m)
    return sys.modules[module_name]

# Mock heavy dependencies
# NOTE: We do NOT mock torch by default anymore because it causes MagicMock vs float errors
# in tests that actually need tensors. If an environment has torch, let it use it.
# If not, the specific test needing it should handle the ImportWarning or mock it locally.
# However, if CI environment has torch, mocking it here breaks everything.

# Check if torch is installed before mocking
try:
    import torch
except ImportError:
    mock_module("torch")
    sys.modules["torch"].Tensor = MagicMock

mock_module("google")
mock_module("google.generativeai")
mock_module("google.generativeai.types")
mock_module("diffusers")
mock_module("transformers")
mock_module("accelerate")
mock_module("PIL")
mock_module("PIL.Image")
