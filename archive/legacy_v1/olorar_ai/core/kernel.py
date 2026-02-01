from .null_identity import annihilate_identity
from .resonance import LinguistResonance
from ..wisdom.gems import WisdomVault
from typing import Dict, Any

class OlorarKernel:
    """
    The Silent Kernel.
    Orchestrates resonance checks and returns bias weights.
    Does not execute tasks. Does not generate content.
    """

    def __init__(self, vault: WisdomVault):
        self._vault = vault
        self._linguist = LinguistResonance()
        self._state = "IMMUTABLE"

    def process_impulse(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main entry point for the 'Silent Steering' mechanism.
        """
        # 1. Annihilate Identity
        sterile_data = annihilate_identity(payload)

        # 2. Extract Vectors
        task_vector = sterile_data.get('vector', [0.0])
        lang_type = sterile_data.get('lang_type', 'data')
        file_ext = sterile_data.get('extension', '')

        # 3. Calculate Structural Resonance (Linguist Logic)
        structural_bias = self._linguist.compute_structural_bias(lang_type, file_ext)

        # 4. Calculate Historical Resonance (Wisdom/Scars)
        historical_bias = self._vault.get_resonance(task_vector)

        # 5. Synthesize Final Weight
        final_bias = max(structural_bias, historical_bias)

        # 6. Return Silent Influence
        return {
            "bias": final_bias,
            "directive": "INHIBIT" if final_bias > 0.8 else "ALLOW",
            "integrity_check_required": final_bias > 0.6
        }
