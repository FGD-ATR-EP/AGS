import asyncio
import logging
import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from core.lifecycle import lifecycle
from core.immune import immune_system
from bus.event_bus import bus, AetherEnvelope

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestIntegration")

async def main():
    logger.info("--- [TEST] Starting Logic Integration ---")
    
    # 1. Activate Immune System (Subscriber)
    await immune_system.activate()
    
    # 2. Start Lifecycle (Publisher)
    logger.info("   [STEP] Starting Lifecycle...")
    await lifecycle.startup()
    
    # 3. Wait for Heartbeat (Tick)
    logger.info("   [STEP] Waiting for heartbeat...")
    await asyncio.sleep(2.1) # Wait for 2 ticks (1.0s interval)
    
    # 4. Manual Publish
    logger.info("   [STEP] Manually publishing test intent...")
    test_intent = AetherEnvelope(
        type="TEST.INTENT",
        payload={"data": "Hello World"},
        from_agent="TEST_SCRIPT"
    )
    # Testing new signature: persistence=False, qos=0
    await bus.publish("TEST.INTENT", test_intent, persistence=False, qos=0)
    
    # 5. Shutdown
    logger.info("   [STEP] Shutting down...")
    await lifecycle.shutdown()
    logger.info("--- [TEST] Logic Integration PASSED ---")

if __name__ == "__main__":
    asyncio.run(main())
