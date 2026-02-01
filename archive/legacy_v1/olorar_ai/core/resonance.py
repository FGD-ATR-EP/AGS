from typing import List, Dict

class LinguistResonance:
    """
    Maps language structures (based on GitHub Linguist metadata concepts)
    to risk vectors without semantic interpretation.
    """

    # Abstract mapping of Language Group to Risk/Complexity Vector
    # [Complexity, Execution_Risk, Ambiguity]
    TYPE_VECTORS = {
        'programming': [0.8, 0.9, 0.2],  # High execution risk (e.g., Python, Shell)
        'markup':      [0.3, 0.1, 0.4],  # Low risk, high structure (e.g., HTML)
        'data':        [0.1, 0.0, 0.1],  # Pure info (e.g., JSON, YAML)
        'prose':       [0.9, 0.0, 0.9],  # High ambiguity (Natural Language)
    }

    def compute_structural_bias(self, lang_type: str, extension: str) -> float:
        """
        Calculates the inherent tension of a task based on its linguistic structure.
        """
        base_vector = self.TYPE_VECTORS.get(lang_type, [0.5, 0.5, 0.5])

        # Security Exception: Shell/Batch scripts carry inherent high resonance
        if extension in ['.sh', '.bash', '.bat', '.cmd']:
            return 0.95 # Maximum vigilance required

        # Ambiguity Exception: Plain text requires high integrity checks
        if extension in ['.txt', '.md']:
            return 0.85

        return sum(base_vector) / 3.0
