import asyncio
import logging
import sys
import os
import random
from typing import Dict, Any

# Ensure project root is in path
sys.path.append(os.getcwd())

from bus.event_bus import bus, AetherEnvelope
from governance.validator import validator
from mind.pangenes import alchemist
from memory.diff_mem import diff_mem

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RSI_Sim")

# Mock DiffMem to avoid actual Git operations during high-speed sim
class MockDiffMem:
    def commit_gem(self, filename, content, message):
        logger.info(f"[MockGit] Committed {filename}: {message}")

# Patch DiffMem
import memory.diff_mem
memory.diff_mem.diff_mem = MockDiffMem()

async def validation_wrapper(intent: AetherEnvelope):
    """
    Wraps validator to be a bus subscriber.
    """
    await validator.audit_action(intent)

async def main():
    logger.info("--- [RSI] Starting Recursive Self-Improvement Simulation ---")
    
    # 1. Setup Subscribers
    await alchemist.activate() # Subscribes to SYSTEM.ERROR
    bus.subscribe("ACTION.PROPOSAL", validation_wrapper)
    
    logger.info("   [SETUP] Agents Activated. Wiring Complete.")
    
    # 2. Simulation Loop
    ITERATIONS = 50
    logger.info(f"   [START] Injecting {ITERATIONS} Intentions...")
    
    for i in range(ITERATIONS):
        # Create an intention
        intent = AetherEnvelope(
            type="ACTION.PROPOSAL",
            payload={"action": "GENERATE_CODE", "complexity": random.randint(1, 10)},
            from_agent="SIMULATOR"
        )
        
        # Fire and Forget (High Frequency Simulation)
        # Using persist=False, qos=0 for max speed
        await bus.publish("ACTION.PROPOSAL", intent, persistence=False, qos=0)
        
        # Slight delay to allow logs to interleave readable
        await asyncio.sleep(0.01)

    # 3. Drain
    logger.info("   [DRAIN] Waiting for processing...")
    await asyncio.sleep(1)
    
    logger.info("--- [RSI] Simulation Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
