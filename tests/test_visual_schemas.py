import pytest
from src.backend.genesis_core.models.visual import VisualParameters, IntentCategory, BaseShape

def test_visual_parameters_validation():
    # Valid
    data = {
        "intent_category": "request",
        "emotional_valence": 0.5,
        "energy_level": 0.8,
        "visual_parameters": {
            "base_shape": "sphere",
            "turbulence": 0.5,
            "particle_density": 0.5,
            "color_palette": "#FF00FF"
        }
    }
    vp = VisualParameters(**data)
    assert vp.intent_category == IntentCategory.REQUEST
    assert vp.visual_parameters.base_shape == BaseShape.SPHERE

def test_visual_parameters_invalid():
    # Invalid Enum
    data = {
        "intent_category": "invalid_category", # Should fail
        "emotional_valence": 0.5,
        "energy_level": 0.8,
        "visual_parameters": {
            "base_shape": "sphere",
            "turbulence": 0.5,
            "particle_density": 0.5,
            "color_palette": "#FF00FF"
        }
    }
    with pytest.raises(Exception):
        VisualParameters(**data)

    # Invalid Range
    data["intent_category"] = "request"
    data["energy_level"] = 1.5 # Should fail (le=1.0)
    with pytest.raises(Exception):
        VisualParameters(**data)
