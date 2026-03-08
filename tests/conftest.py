import sys
import asyncio
import inspect
from unittest.mock import MagicMock
import pytest

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

# Mock heavy dependencies (only when unavailable)
try:
    import torch  # noqa: F401
except Exception:
    mock_module("torch")
mock_module("google")
mock_module("google.generativeai")
mock_module("google.generativeai.types")
mock_module("diffusers")
mock_module("transformers")
mock_module("accelerate")
mock_module("PIL")
mock_module("PIL.Image")

# Mock classes often used in type hints (only for mocked torch)
if isinstance(sys.modules.get("torch"), MagicMock):
    sys.modules["torch"].Tensor = MagicMock


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem):
    """Minimal asyncio runner for environments without pytest-asyncio."""
    if "asyncio" not in pyfuncitem.keywords:
        return None

    testfunction = pyfuncitem.obj
    if inspect.iscoroutinefunction(testfunction):
        asyncio.run(testfunction(**pyfuncitem.funcargs))
        return True

    return None
