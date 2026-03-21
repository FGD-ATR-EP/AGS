import time
from enum import Enum

class ConsciousnessState(Enum):
    NIRODHA = "Nirodha"
    AWAKENED = "Awakened"
    TRANSITION = "Transition"

class AwakeningCycleAuditor:
    def __init__(self):
        self.current_state = ConsciousnessState.NIRODHA
        self.state_start_time = time.time()
        self.transition_log = []

    def update_state(self, new_state_str: str):
        try:
            # Normalize string
            s = new_state_str.capitalize()
            # Map known states
            if s not in [e.value for e in ConsciousnessState]:
                return

            new_state = ConsciousnessState(s)
        except ValueError:
            return

        if new_state != self.current_state:
            duration = time.time() - self.state_start_time
            self.transition_log.append({
                "from": self.current_state.value,
                "to": new_state.value,
                "duration": duration,
                "timestamp": time.time()
            })
            self.current_state = new_state
            self.state_start_time = time.time()

    def monitor_consciousness_cycle(self):
        duration = time.time() - self.state_start_time

        # Detect State Lock
        is_locked = False
        if self.current_state == ConsciousnessState.TRANSITION and duration > 300:
            is_locked = True

        return {
            "type": "consciousness",
            "metrics": {
                "current_state": self.current_state.value,
                "state_duration_sec": duration,
                "state_lock_detected": 1.0 if is_locked else 0.0,
                "nirodha_depth": 1.0 if self.current_state == ConsciousnessState.NIRODHA else 0.0
            }
        }
