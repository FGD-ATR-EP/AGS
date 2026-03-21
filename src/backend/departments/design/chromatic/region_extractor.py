import torch
from typing import Tuple
from src.backend.genesis_core.logenesis.correction_schemas import SpatialMask

class RegionExtractor:
    def __init__(self, frame_shape: Tuple[int, int, int]):
        # Expecting (H, W, C)
        self.h, self.w, _ = frame_shape

    def validate(self, mask: SpatialMask) -> bool:
        return (0 <= mask.x_min < mask.x_max <= self.w) and (0 <= mask.y_min < mask.y_max <= self.h)

    def extract(self, frame: torch.Tensor, mask: SpatialMask) -> torch.Tensor:
        """
        Extracts the region from the frame.
        Assumes frame is [C, H, W]
        """
        if not self.validate(mask):
            raise ValueError("Mask out of bounds")
        return frame[:, mask.y_min:mask.y_max, mask.x_min:mask.x_max].clone()

    def merge(self, full: torch.Tensor, updated_region: torch.Tensor, mask: SpatialMask) -> torch.Tensor:
        """
        Merges the updated region back into the full frame with a blend.
        Assumes full and updated_region are [C, H, W] (region dimensions for updated_region)
        """
        x1, y1, x2, y2 = mask.x_min, mask.y_min, mask.x_max, mask.y_max

        # Create a horizontal blend mask (0 to 1)
        # Shape: (H_region, W_region)
        blend = torch.linspace(0, 1, steps=x2-x1).unsqueeze(0).expand(y2-y1, -1).to(full.device)

        # Broadcast blend to match channels if necessary, or let implicit broadcasting work.
        # full slice: [C, H_reg, W_reg]
        # blend: [H_reg, W_reg] -> broadcasts to [1, H_reg, W_reg] -> works against C.

        full[:, y1:y2, x1:x2] = full[:, y1:y2, x1:x2] * (1 - blend) + updated_region * blend
        return full
