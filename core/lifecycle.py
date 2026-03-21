import asyncio
import logging
from bus.event_bus import bus
from bus.intent import create_intent

logger = logging.getLogger("Lifecycle")

class LifecycleManager:
    """
    The Heartbeat of Existence.
    Manages the awakening and nirodha (shutdown) of the system.
    """
    def __init__(self, tick_rate: float = 1.0):
        self.tick_interval = tick_rate
        self.is_running = False

    async def startup(self):
        """
        The Awakening Ritual.
        """
        logger.info("[Lifecycle] Initiating Startup Sequence...")
        self.is_running = True
        
        # Announce awakening to the bus
        init_intent = create_intent(
            type="SYSTEM.STARTUP",
            payload={"status": "AWAKENING"},
            from_agent="LIFECYCLE"
        )
        await bus.publish("SYSTEM.STARTUP", init_intent)
        
        # Start the heartbeat loop
        asyncio.create_task(self._heartbeat_loop())
        logger.info("[Lifecycle] System is now ALIVE.")

    async def shutdown(self):
        """
        Graceful shutdown (Nirodha).
        """
        logger.info("[Lifecycle] Initiating Shutdown Sequence...")
        self.is_running = False
        
        shutdown_intent = create_intent(
            type="SYSTEM.SHUTDOWN",
            payload={"status": "SHUTDOWN"},
            from_agent="LIFECYCLE"
        )
        await bus.publish("SYSTEM.SHUTDOWN", shutdown_intent)
        logger.info("[Lifecycle] System has entered NIRODHA state.")

    async def _heartbeat_loop(self):
        """
        The continuous pulse of the system.
        """
        while self.is_running:
            # logger.debug("[Lifecycle] Tick...")
            tick_intent = create_intent(
                type="SYSTEM.TICK",
                payload={"tick": asyncio.get_running_loop().time()},
                from_agent="LIFECYCLE"
            )
            await bus.publish("SYSTEM.TICK", tick_intent)
            await asyncio.sleep(self.tick_interval)

# Instance
lifecycle = LifecycleManager()
