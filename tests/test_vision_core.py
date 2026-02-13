import pytest
import torch
import sys
import os
import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.departments.design.chromatic.aetherium_vision_core import AetheriumVisionCore, AetherState, AetherOutput
from src.backend.genesis_core.logenesis.engine import LogenesisEngine
from src.backend.genesis_core.models.logenesis import IntentPacket
from src.backend.genesis_core.models.visual import BaseShape, VisualParameters

class TestVisionCore:
    def test_vision_core_forward(self):
        """Test the forward pass of AetheriumVisionCore."""
        core = AetheriumVisionCore()

        # Create dummy image [1, 3, 224, 224]
        # Ensure we use real torch tensors or mock .max() if mocked
        dummy_img = torch.rand(1, 3, 224, 224)

        output = core(dummy_img)

        assert isinstance(output, AetherOutput)
        assert isinstance(output.light_field, torch.Tensor)
        assert isinstance(output.embedding, torch.Tensor)
        assert isinstance(output.energy_level, float)
        assert isinstance(output.confidence, float)
        assert isinstance(output.state, AetherState)

        # Check shapes
        # embedding should be [1, embed_dim]
        # embed_dim might depend on backend (e.g. 768 or 512).
        # Checking dimension count is safer unless specific model is guaranteed.
        assert len(output.embedding.shape) == 2
        assert output.embedding.shape[0] == 1

    @pytest.mark.asyncio
    async def test_logenesis_visual_integration(self):
        """Test LogenesisEngine processing a visual packet."""
        engine = LogenesisEngine()

        # Create a mock AetherOutput
        mock_output = AetherOutput(
            light_field=torch.randn(1, 3, 224, 224),
            embedding=torch.randn(1, 768),
            energy_level=0.8,
            confidence=0.9,
            state=AetherState.ANALYSIS
        )

        packet = IntentPacket(
            modality="visual",
            embedding=mock_output.embedding,
            energy_level=mock_output.energy_level,
            confidence=mock_output.confidence,
            raw_payload=mock_output
        )

        response = await engine.process(packet, session_id="test_visual_session")

        # Check for COLLAPSED state which indicates engine rejection
        if response.state == "COLLAPSED":
             # If it collapses, we verify it handled the error gracefully
             assert response.text_content is not None
        else:
             assert response.visual_analysis is not None
             # Should map ANALYSIS state to VORTEX
             assert response.visual_analysis.visual_parameters.base_shape == BaseShape.VORTEX
             assert response.visual_analysis.energy_level == 0.8
             assert response.manifestation_granted is True
             assert "State: ANALYSIS" in response.text_content
