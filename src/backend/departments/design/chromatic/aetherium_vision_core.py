import logging
from typing import Tuple, Optional, Union
import numpy as np
from dataclasses import dataclass
from src.backend.genesis_core.state.aether_state import AetherState, AetherOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- TORCH / MOCK IMPORT BLOCK ---
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    try:
        from unittest.mock import Mock
    except Exception:
        Mock = tuple()
    TORCH_AVAILABLE = not isinstance(torch, Mock)
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Disable MPS for mixed precision stability as per instruction
    # if torch.backends.mps.is_available(): DEVICE = torch.device("mps")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("Torch not found. Using Mock Vision Core.")

    class MockModule:
        """
        A lightweight shim for torch.nn.Module to allow execution in headless/mobile environments
        where PyTorch is not available.
        """
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
            """
            Mimics nn.Module.__call__ by delegating to forward() if it exists.
            This allows instances to be used as functors.
            """
            if hasattr(self, "forward"):
                return self.forward(*args, **kwargs)
            return None

        def register_buffer(self, name, tensor):
            setattr(self, name, tensor)

        def to(self, device):
            return self

    class MockNN:
        Module = MockModule
        class Conv2d(MockModule):
            def __init__(self, *args, **kwargs):
                self.weight = type('MockWeight', (), {'copy_': lambda s, x: None})()
                super().__init__()
        class BatchNorm2d(MockModule): pass
        class Linear(MockModule): pass
        class AdaptiveAvgPool2d(MockModule): pass
        class LayerNorm(MockModule): pass

    class MockTorch:
        def device(self, x): return x
        def tensor(self, x, **kwargs): return np.array(x)
        def from_numpy(self, x): return x
        def cat(self, tensors, dim=0): return tensors[0] if tensors else None
        def sigmoid(self, x): return x
        def randn(self, *args): return np.zeros(args)
        class no_grad:
            def __enter__(self): pass
            def __exit__(self, *args): pass
        float32 = "float32"

    class MockF:
        def normalize(self, x, **kwargs): return x
        def relu(self, x, **kwargs): return x
        def conv2d(self, x, **kwargs): return x

    nn = MockNN()
    torch = MockTorch()
    F = MockF()
    DEVICE = "cpu"

logger.info(f"Using device: {DEVICE}")

@dataclass
class BioVisionConfig:
    dog_sigma_center: float = 1.0
    dog_sigma_surround: float = 3.0
    dog_kernel_size: int = 15
    embed_dim: int = 768
    seq_len: int = 5
    use_mixed_precision: bool = True
    input_size: Tuple[int, int] = (224, 224)

CONFIG = BioVisionConfig()

class OpticalPreprocessing(nn.Module):
    """Normalize and prepare dimensions."""
    def forward(self, x):
        # Expect input [B, C, H, W] values 0-1 or 0-255
        if hasattr(x, "max") and x.max() > 1.0:
            x = x / 255.0
        if TORCH_AVAILABLE:
            return F.normalize(x, p=2, dim=1)
        return x

class PhotoreceptorSimulation(nn.Module):
    def __init__(self, config: BioVisionConfig = CONFIG):
        super().__init__()
        self.config = config
        self.register_buffer(
            "dog_kernel",
            self._create_dog_kernel(
                config.dog_sigma_center,
                config.dog_sigma_surround,
                config.dog_kernel_size
            )
        )

    def _create_dog_kernel(self, sigma1: float, sigma2: float, size: int):
        if size % 2 == 0:
            size += 1

        x, y = np.mgrid[-(size//2):(size//2)+1, -(size//2):(size//2)+1]
        g1 = np.exp(-(x*x + y*y) / (2.0 * sigma1*sigma1))
        g2 = np.exp(-(x*x + y*y) / (2.0 * sigma2*sigma2))
        dog = g1 - g2
        dog = dog / dog.sum()
        if TORCH_AVAILABLE:
            dog = torch.from_numpy(dog).float()
            return dog.unsqueeze(0).unsqueeze(0)
        return dog

    def forward(self, x):
        if not TORCH_AVAILABLE:
            return x

        r, g, b = x[:, 0:1], x[:, 1:2], x[:, 2:3]
        y = (r + g) * 0.5
        rg = r - g
        by = b - y
        lum = y

        opponent = torch.cat([rg, by, lum], dim=1)

        kernel = self.dog_kernel.to(x.device).expand(3, 1, -1, -1)
        dog = F.conv2d(
            opponent,
            weight=kernel,
            padding=self.config.dog_kernel_size//2,
            groups=3
        )
        return dog

class RetinalNeuralProcessing(nn.Module):
    def __init__(self, out_channels_per_dir: int = 16):
        super().__init__()
        self.out_channels = out_channels_per_dir

        self.edge_h = nn.Conv2d(3, out_channels_per_dir, 3, padding=1, bias=False)
        self.edge_v = nn.Conv2d(3, out_channels_per_dir, 3, padding=1, bias=False)
        self.bn = nn.BatchNorm2d(out_channels_per_dir * 2)

        self._init_sobel_kernels()

    def _init_sobel_kernels(self):
        sobel_h = torch.tensor([[-1,0,1], [-2,0,2], [-1,0,1]], dtype=torch.float32)
        sobel_v = torch.tensor([[-1,-2,-1], [0,0,0], [1,2,1]], dtype=torch.float32)

        if TORCH_AVAILABLE:
            sobel_h = sobel_h.view(1, 1, 3, 3).repeat(1, 3, 1, 1)
            sobel_v = sobel_v.view(1, 1, 3, 3).repeat(1, 3, 1, 1)

        with torch.no_grad():
            if TORCH_AVAILABLE:
                self.edge_h.weight.copy_(sobel_h.repeat(self.out_channels, 1, 1, 1))
                self.edge_v.weight.copy_(sobel_v.repeat(self.out_channels, 1, 1, 1))

    def forward(self, x):
        if not TORCH_AVAILABLE:
            return x
        h = F.relu(self.edge_h(x), inplace=True)
        v = F.relu(self.edge_v(x), inplace=True)
        edges = torch.cat([h, v], dim=1)
        return self.bn(edges)

class CognitiveLoadEstimator(nn.Module):
    def __init__(self, embed_dim: int):
        super().__init__()
        self.fc = nn.Linear(embed_dim, 1)

    def forward(self, emb):
        if not TORCH_AVAILABLE:
            return 0.5 # Default load
        return torch.sigmoid(self.fc(emb))

class CorticalReasoningLayer(nn.Module):
    def __init__(self, in_channels: int, embed_dim: int):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(in_channels, embed_dim)
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x):
        if not TORCH_AVAILABLE:
            # Return dummy embedding
            return torch.randn(x.shape[0], 768) if hasattr(x, "shape") else np.zeros((1, 768))

        x = self.pool(x).flatten(1)
        emb = self.norm(self.fc(x))
        return emb

class AetheriumVisionCore(nn.Module):
    def __init__(self, config: BioVisionConfig = CONFIG):
        super().__init__()
        self.optical = OpticalPreprocessing()
        self.photoreceptor = PhotoreceptorSimulation(config)
        self.retinal = RetinalNeuralProcessing()
        self.cortical = CorticalReasoningLayer(
            in_channels=32,
            embed_dim=config.embed_dim
        )
        self.load_estimator = CognitiveLoadEstimator(config.embed_dim)

    def forward(self, x) -> AetherOutput:
        # PERCEPTION
        x = self.optical(x)
        x = self.photoreceptor(x)
        x = self.retinal(x)

        # ANALYSIS
        emb = self.cortical(x)

        if TORCH_AVAILABLE:
            load = self.load_estimator(emb).mean().item()
        else:
            load = 0.5 # Default

        # STATE DECISION
        if load < 0.2:
            state = AetherState.STABILIZED
        elif load < 0.5:
            state = AetherState.PERCEPTION
        else:
            state = AetherState.ANALYSIS

        confidence = 1.0 - load

        return AetherOutput(
            light_field=x,
            embedding=emb,
            energy_level=load,
            confidence=confidence,
            state=state
        )
