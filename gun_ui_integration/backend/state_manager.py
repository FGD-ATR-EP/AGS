class StateManager:
    def __init__(self):
        self.state = "idle"
        self.color = "#00F3FF" # Cyan (Aetherium Default)

    def update_state(self, new_state):
        valid_states = ["idle", "processing", "error", "awakened"]
        if new_state not in valid_states:
            return False

        self.state = new_state
        # Mapping State -> Color
        if new_state == "idle":
            self.color = "#00F3FF" # Cyan
        elif new_state == "processing":
            self.color = "#FF00E6" # Magenta (Thinking)
        elif new_state == "error":
            self.color = "#FF0000" # Red
        elif new_state == "awakened":
            self.color = "#FFFFFF" # White Core

        return True
