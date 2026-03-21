from enum import Enum
from dataclasses import dataclass
from typing import Any
try:
    import torch
    Tensor = torch.Tensor
except ImportError:
    torch = None
    Tensor = Any

class AetherState(Enum):
    IDLE = 0
    PERCEPTION = 1
    ANALYSIS = 2
    MANIFESTATION = 3
    STABILIZED = 4

@dataclass
class AetherOutput:
    light_field: Tensor
    embedding: Tensor
    energy_level: float
    confidence: float
    state: AetherState
