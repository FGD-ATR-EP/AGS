import asyncio
import logging
import inspect
import uuid
from typing import Dict, Callable, Awaitable, Set, Any
from src.backend.genesis_core.protocol.schemas import AetherEvent
from src.backend.genesis_core.bus.base import BaseAetherBus

logger = logging.getLogger("AetherBusExtreme")

class AetherBusExtreme(BaseAetherBus):
    """
    Concrete implementation of the AetherBus using AsyncIO for the internal Data Plane.
    Acts as the high-speed nervous system for Aetherium.
    """
    def __init__(self):
        # session_id -> callback
        self._subscribers: Dict[str, Callable[[AetherEvent], Awaitable[None]]] = {}
        self._global_listeners: Set[Callable[[AetherEvent], Awaitable[None]]] = set()
        self._running = False

    async def connect(self):
        self._running = True
        logger.info("🚀 [AetherBusExtreme] Connected (AsyncIO Mode).")

    async def close(self):
        self._running = False
        self._subscribers.clear()
        self._global_listeners.clear()
        logger.info("🛑 [AetherBusExtreme] Closed.")

    def write(self, topic: str, payload: Any) -> str:
        """
        Legacy compatibility method for synchronous writing.
        Wraps the payload in an AetherEvent and schedules it.
        """
        msg_id = str(uuid.uuid4())

        # In Web-Native Mode, we wrap everything in AetherEvent
        from src.backend.genesis_core.protocol.schemas import AetherEventType

        # Determine target session (topic based)
        target_session = topic
        if topic == "system.broadcast":
            target_session = "*"

        event = AetherEvent(
            type=AetherEventType.STATE_UPDATE,
            session_id=target_session
        )
        event.extensions["raw_payload"] = payload
        event.extensions["topic"] = topic

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event))
        except RuntimeError:
            pass

        return msg_id

    async def publish(self, event: AetherEvent):
        """
        Dispatches the event to relevant subscribers.
        """
        if not self._running:
            return

        tasks = []

        def add_task(cb, evt):
            try:
                if inspect.iscoroutinefunction(cb):
                    tasks.append(cb(evt))
                elif asyncio.iscoroutine(cb):
                     tasks.append(cb)
                else:
                     res = cb(evt)
                     if inspect.isawaitable(res):
                         tasks.append(res)
                     else:
                         async def _wrap(): return res
                         tasks.append(_wrap())
            except Exception as e:
                logger.error(f"Error preparing callback: {e}")

        # 1. Targeted Delivery
        if event.session_id:
            if event.session_id in self._subscribers:
                add_task(self._subscribers[event.session_id], event)
            elif event.session_id == "*":
                # Broadcast
                for callback in self._subscribers.values():
                    add_task(callback, event)
            else:
                pass

        # 2. Global Broadcast
        if event.session_id is None:
            for callback in self._subscribers.values():
                add_task(callback, event)

        # 3. Global Listeners
        for listener in self._global_listeners:
            add_task(listener, event)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def subscribe(self, session_id: str, callback: Callable[[AetherEvent], Awaitable[None]]):
        if session_id in self._subscribers:
            logger.warning(f"⚠️ [AetherBusExtreme] Session {session_id} already subscribed. Overwriting.")
        self._subscribers[session_id] = callback
        logger.debug(f"🔗 [AetherBusExtreme] Subscribed session: {session_id}")

    async def unsubscribe(self, session_id: str):
        if session_id in self._subscribers:
            del self._subscribers[session_id]
            logger.debug(f"🔌 [AetherBusExtreme] Unsubscribed session: {session_id}")

    async def add_global_listener(self, callback: Callable[[AetherEvent], Awaitable[None]]):
        """For system-wide logging or diagnostics."""
        self._global_listeners.add(callback)
