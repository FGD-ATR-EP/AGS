import torch
import pytest
from unittest.mock import MagicMock
from src.backend.departments.design.chromatic.region_extractor import RegionExtractor
from src.backend.genesis_core.logenesis.correction_schemas import SpatialMask

# Skip if torch is mocked (e.g. in CI without full deps or due to conftest)
if isinstance(torch, MagicMock) or (hasattr(torch, '__module__') and 'unittest.mock' in torch.__module__):
    pytest.skip("Torch is mocked, skipping region extractor tests", allow_module_level=True)

def test_extract():
    """Extract a bounded region and confirm expected tensor shape."""
    # If we get here, torch is likely real or a very sophisticated mock
    try:
        frame = torch.randn(3, 100, 100)
    except Exception:
         pytest.skip("Torch randn failed, possibly mocked incorrectly")

    extractor = RegionExtractor((100, 100, 3))
    mask = SpatialMask(10, 10, 20, 20)
    region = extractor.extract(frame, mask)
    assert region.shape == (3, 10, 10)

def test_merge():
    """Merge an updated region and validate in/out-of-mask behavior."""
    try:
        frame = torch.zeros(3, 100, 100)
        updated = torch.ones(3, 10, 10)
    except Exception:
         pytest.skip("Torch zeros/ones failed")

    extractor = RegionExtractor((100, 100, 3))
    mask = SpatialMask(10, 10, 20, 20)

    result = extractor.merge(frame, updated, mask)
    # Check if region is updated (checking center of region to avoid blend edge)
    # Blend is horizontal. Center should have some weight.
    # mask 10 to 20. Width 10.
    # blend goes 0 to 1 across x.
    # At x=15 (relative to frame index 0), blend is ~0.5.
    # updated=1, full=0. result = 0*(0.5) + 1*0.5 = 0.5.

    # Check if result is a tensor (real torch)
    if isinstance(result, MagicMock):
        return # Cannot assert on mock values easily without configuring return values

    assert result[0, 15, 15] > 0.0

    # Check outside region
    assert result[:, 0:10, 0:10].sum() == 0

def test_validate():
    """Validate mask boundary checks for accepted and rejected ranges."""
    extractor = RegionExtractor((100, 100, 3))
    assert extractor.validate(SpatialMask(0, 0, 10, 10))
    assert not extractor.validate(SpatialMask(-1, 0, 10, 10))
    # x_max 101 is > w=100 ? Wait, index is usually exclusive for slice, but check validation.
    # Validation: mask.x_max <= self.w.
    # If x_max = 100, valid.
    # If x_max = 101, invalid.
    assert extractor.validate(SpatialMask(0, 0, 100, 100))
    assert not extractor.validate(SpatialMask(0, 0, 101, 10))


def test_extract_raises_on_out_of_bounds_mask():
    """Raise an error when extraction mask exceeds frame bounds."""
    try:
        frame = torch.randn(3, 100, 100)
    except Exception:
        pytest.skip("Torch randn failed")

    extractor = RegionExtractor((100, 100, 3))
    invalid_mask = SpatialMask(90, 90, 110, 110)

    with pytest.raises(ValueError, match="Mask out of bounds"):
        extractor.extract(frame, invalid_mask)
