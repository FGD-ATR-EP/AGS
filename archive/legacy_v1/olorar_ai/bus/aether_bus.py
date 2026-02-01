class AetherBus:
    """
    Single-direction transport layer.
    Ensures decoupling between Platforms (Masks) and Core.
    """
    def __init__(self):
        self._core_link = None

    def connect_core(self, core_instance):
        self._core_link = core_instance

    def dispatch_vector(self, payload: dict) -> dict:
        if not self._core_link:
            # Fail-safe: If core is unreachable, default to maximum caution
            return {"bias": 1.0, "directive": "HALT"}

        # Transmit to Core
        return self._core_link.process_impulse(payload)
