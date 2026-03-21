class LivingGunUIAuditor:
    def __init__(self):
        pass

    def audit_living_skin(self, last_visual_params: dict):
        """Analyzes the life-signs of the interface based on sent visual parameters."""
        report = {
            "type": "interface",
            "metrics": {
                "light_responsiveness": 0.0,
                "bio_compatibility": 0.0,
                "emotional_signal_fidelity": 0.0
            }
        }

        if last_visual_params:
            # Check if parameters are within "biological" ranges
            # Energy should be 0.0 - 1.0
            energy = last_visual_params.get("energy", 0)
            if 0.0 <= energy <= 1.0:
                report["metrics"]["light_responsiveness"] = 1.0

            # Emotional Valence should be -1.0 to 1.0 or similar
            # If we have valence, check it.
            # Assuming params might be nested or flat.

            report["metrics"]["bio_compatibility"] = 1.0

        return report
