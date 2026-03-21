from dataclasses import dataclass
from typing import Dict, Any, List
import random

@dataclass
class CognitiveState:
    valence: float  # -1.0 to 1.0 (Negative to Positive)
    arousal: float  # 0.0 to 1.0 (Calm to Excited)
    entropy: float  # 0.0 to 1.0 (Order to Chaos)

class LogenesisEngine:
    """
    The reasoning core that processes 'shape' and 'dynamics' of intent.
    morphological reasoning.
    """
    def __init__(self):
        self.current_state = CognitiveState(valence=0.0, arousal=0.5, entropy=0.1)

    def process_intent_shape(self, text_input: str) -> CognitiveState:
        """
        Analyzes the text input to determine the morphological shape of the intent.
        (Simplified logic for demonstration)
        """
        # In a real system, this would use sentiment analysis and complexity metrics.
        length = len(text_input)
        
        # Valence heuristic
        if "error" in text_input.lower() or "fail" in text_input.lower():
            self.current_state.valence = max(-1.0, self.current_state.valence - 0.2)
        elif "success" in text_input.lower() or "good" in text_input.lower():
            self.current_state.valence = min(1.0, self.current_state.valence + 0.2)
            
        # Arousal based on length/complexity
        if length > 100:
            self.current_state.arousal = min(1.0, self.current_state.arousal + 0.1)
        else:
            self.current_state.arousal = max(0.0, self.current_state.arousal - 0.05)
            
        # Entropy - Random flux for "life-like" jitter
        self.current_state.entropy = random.uniform(0.0, 0.2)
        
        return self.current_state

    def get_cognitive_dsl(self) -> Dict[str, Any]:
        """
        Returns the state in a format suitable for GunUI visualization.
        """
        return {
            "valence": self.current_state.valence,
            "energy": self.current_state.arousal,
            "turbulence": self.current_state.entropy,
            "state_phase": "CRYSTALLIZATION" if self.current_state.entropy < 0.1 else "DISSOLUTION"
        }
