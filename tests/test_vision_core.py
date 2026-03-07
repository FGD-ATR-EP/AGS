import pytest
import torch
import sys
import os
import asyncio
from typing import Any

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
        assert output.embedding.shape == (1, 768)

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

        assert response.visual_analysis is not None
        # Should map ANALYSIS state to VORTEX
        assert response.visual_analysis.visual_parameters.base_shape == BaseShape.VORTEX
        assert response.visual_analysis.energy_level == 0.8

        # Verify Manifestation Gate allowed it (ANALYSIS + High Energy usually passes or handled by visual path)
        # Note: Logic for visual packet in engine sets visual_params directly.
        # But `_check_manifestation_gate` runs on it.
        # Energy 0.8 > 0.6, so it should pass if treated as CHAT.
        assert response.manifestation_granted is True

        # Verify text content
        assert "State: ANALYSIS" in response.text_content
