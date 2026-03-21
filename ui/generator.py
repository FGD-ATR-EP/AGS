from mind.reasoning import CognitiveState
from typing import Dict, Any, Tuple

class ChromaticGenerator:
    """
    The Manifestation of Intent.
    Translates Logenesis cognitive states into visual parameters (GunUI).
    """
    
    def translate_state(self, state: CognitiveState) -> Dict[str, Any]:
        """
        Maps cognitive metrics to the Chromatic Language.
        """
        # 1. Color Mapping
        color_hex = self._get_color(state.valence, state.arousal)
        
        # 2. Form Mapping
        form_type = "SPHERE" if state.entropy < 0.1 else "VORTEX"
        
        # 3. Particle Dynamics
        speed = 0.5 + (state.arousal * 2.0)
        
        return {
            "primary_color": color_hex,
            "geometry": form_type,
            "particle_speed": speed,
            "turbulence_factor": state.entropy * 10
        }

    def _get_color(self, valence: float, arousal: float) -> str:
        """
        Determines the color based on emotional state.
        Purple: Deep Reasoning (High Arousal, Neutral Valence)
        Electric Blue: Processing (High Arousal, Positive Valence)
        White: Neutral / Pure
        Red: Error / Danger (Negative Valence)
        """
        if valence < -0.5:
            return "#FF0000" # Red (Danger)
        
        if arousal > 0.7:
            if valence > 0.0:
                return "#00FFFF" # Electric Blue
            else:
                return "#800080" # Purple (Deep Thought/Empathy)
                
        return "#FFFFFF" # White

gun_ui = ChromaticGenerator()
