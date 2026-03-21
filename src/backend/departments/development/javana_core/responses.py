# JAVANA: Pre-baked Reflex Responses
# "Zero-latency visual feedback."

# Pre-defined Visual Parameter dictionaries.
# These bypass the EmbodimentAdapter and IntentInterpreter.
# Format adheres to src.backend.core.visual_schemas.VisualParameters (JSON serialized form)

REFLEX_PARAMS = {
    "SHIELD": {
        "intent_category": "command",
        "emotional_valence": 0.5, # Positive/Safe
        "energy_level": 1.0,      # Max Energy
        "semantic_concepts": ["shield", "protect", "reflex"],
        "visual_parameters": {
            "base_shape": "sphere",
            "turbulence": 0.0,        # Solid, stable shield
            "particle_density": 1.0,  # Maximum density
            "color_palette": "#06b6d4", # Cyan
            "flow_direction": "outward"
        }
    },
    "STABILIZE": {
        "intent_category": "chat", # Neutral
        "emotional_valence": 0.0,
        "energy_level": 0.2,      # Low energy (Calm)
        "semantic_concepts": ["stabilize", "calm", "dampen"],
        "visual_parameters": {
            "base_shape": "cube",     # Structure/Order
            "turbulence": 0.0,        # Zero chaos
            "particle_density": 0.5,
            "color_palette": "#FFFFFF", # White
            "flow_direction": "none"
        }
    },
    "FLASH": {
        "intent_category": "command",
        "emotional_valence": 0.0,
        "energy_level": 1.0,      # Max Intensity
        "semantic_concepts": ["startle", "flash"],
        "visual_parameters": {
            "base_shape": "scatter",  # Burst effect
            "turbulence": 1.0,        # High Chaos
            "particle_density": 0.8,
            "color_palette": "#FFFFFF", # Bright White
            "flow_direction": "outward"
        }
    }
}
