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
mock_module("torch")
mock_module("google")
mock_module("google.generativeai")
mock_module("google.generativeai.types")
mock_module("diffusers")
mock_module("transformers")
mock_module("accelerate")
mock_module("PIL")
mock_module("PIL.Image")

# Mock classes often used in type hints
sys.modules["torch"].Tensor = MagicMock
