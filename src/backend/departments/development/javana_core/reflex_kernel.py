import math
import time
from typing import Optional
from .shared_mem import JavanaMemory

# JAVANA: The Reflex Kernel
# "Think faster than thought."

class JavanaKernel:
    """
    The spinal cord of the system.
    Processes raw sensor data and triggers immediate reflex actions.
    Bypasses the Logenesis Engine entirely.
    """
    __slots__ = ('memory', 'last_x', 'last_y', 'last_tick')

    def __init__(self):
        self.memory = JavanaMemory()
        # Initialize last known position (center)
        self.last_x = 0.5
        self.last_y = 0.5
        self.last_tick = time.perf_counter()
        print("⚡ [JAVANA] Reflex System: ONLINE (Raw Speed Mode)")

    def update_sensors(self, energy: float = 0.0, x: float = 0.5, y: float = 0.5, turbulence: float = 0.0):
        """
        Updates the shared memory block with the latest sensor data.
        """
        self.memory.write(energy, x, y, turbulence)

    def fast_react(self) -> Optional[str]:
        """
        Executes the reflex arc logic.
        Returns a string command key (e.g., "SHIELD") if a reflex is triggered, else None.
        This function is designed to run in < 1ms.
        """
        # 1. Read directly from "Memory" (Zero-copy simulation)
        energy, x, y, turbulence = self.memory.read()

        # 2. Reflex Logic (The "If-This-Then-That" of survival)

        # --- REFLEX 1: THE SHIELD (High Energy Impact) ---
        # Triggered by loud sounds or sudden high-energy input.
        if energy > 0.9:
            return "SHIELD"

        # --- REFLEX 2: THE DAMPENER (System Instability) ---
        # Triggered when visual turbulence exceeds safety thresholds.
        if turbulence > 0.95:
            return "STABILIZE"

        # --- REFLEX 3: THE STARTLE (Rapid Movement) ---
        # Triggered by fast cursor/gaze movement across the screen.
        dx = x - self.last_x
        dy = y - self.last_y
        # Fast approximate distance (Euclidean)
        # Optimization: Compare squared distance to avoid sqrt?
        # dist_sq = dx*dx + dy*dy; threshold_sq = 0.64 (0.8^2)
        dist_sq = dx*dx + dy*dy

        # Update state for next tick (Side Effect)
        self.last_x = x
        self.last_y = y

        if dist_sq > 0.64: # 0.8 * 0.8
            return "FLASH"

        return None
