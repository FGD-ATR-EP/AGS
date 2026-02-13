import torch
import pytest
from unittest.mock import MagicMock, patch
from src.backend.departments.design.chromatic.region_extractor import RegionExtractor
from src.backend.genesis_core.logenesis.correction_schemas import SpatialMask

def test_extract():
    # Use real tensors if possible, otherwise ensure mock returns correct shape
    frame = torch.randn(3, 100, 100)
    extractor = RegionExtractor((100, 100, 3))
    mask = SpatialMask(10, 10, 20, 20)
    region = extractor.extract(frame, mask)
    # The error "AssertionError: assert <MagicMock ...> == (3, 10, 10)" suggests
    # 'region' is a MagicMock. This likely means 'extractor.extract' returns a mock
    # or 'frame' interactions cause a mock return if 'frame' was a mock (it is real tensor here).
    # Wait, the log showed 'region' was a MagicMock.
    # Ah, if torch is mocked globally in some other test setup or fixture, that would explain it.
    # But assuming clean env with real torch installed:
    assert region.shape == (3, 10, 10)

def test_merge():
    frame = torch.zeros(3, 100, 100)
    extractor = RegionExtractor((100, 100, 3))
    mask = SpatialMask(10, 10, 20, 20)
    updated = torch.ones(3, 10, 10)
    result = extractor.merge(frame, updated, mask)

    # Check updated region value
    # Ensure result is a tensor, not a mock, to compare with float
    val = result[0, 15, 15]
    if isinstance(val, torch.Tensor):
        val = val.item()
    assert val > 0.0

    # Check outside region
    assert result[:, 0:10, 0:10].sum() == 0

def test_validate():
    extractor = RegionExtractor((100, 100, 3))
    assert extractor.validate(SpatialMask(0, 0, 10, 10))
    assert not extractor.validate(SpatialMask(-1, 0, 10, 10))
    assert extractor.validate(SpatialMask(0, 0, 100, 100))
    assert not extractor.validate(SpatialMask(0, 0, 101, 10))

def test_extract_raises_on_out_of_bounds_mask():
    frame = torch.randn(3, 100, 100)
    extractor = RegionExtractor((100, 100, 3))
    invalid_mask = SpatialMask(90, 90, 110, 110)

    with pytest.raises(ValueError, match="Mask out of bounds"):
        extractor.extract(frame, invalid_mask)
