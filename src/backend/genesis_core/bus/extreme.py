import asyncio
import inspect
import logging
import warnings
from typing import Awaitable, Callable, Dict, Set

from src.backend.genesis_core.bus.base import BaseAetherBus
from src.backend.genesis_core.bus.contracts import BusConfig
from src.backend.genesis_core.protocol.schemas import AetherEvent

logger = logging.getLogger("AetherBusExtreme")


class AetherBusExtreme(BaseAetherBus):
    """
    Legacy in-process compatibility implementation.
    Deprecated as the default runtime in favor of Tachyon-backed transport.
    """

    def __init__(self, config: BusConfig | None = None):
        super().__init__(config=config)
        self._subscribers: Dict[str, Callable[[AetherEvent], Awaitable[None]]] = {}
        self._global_listeners: Set[Callable[[AetherEvent], Awaitable[None]]] = set()

    async def connect(self):
        self._running = True
        warnings.warn(
            "AetherBusExtreme is a legacy compatibility path. Configure BUS_IMPLEMENTATION=tachyon for canonical runtime.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.info("AetherBusExtreme connected in compatibility mode.")

    async def close(self):
        self._running = False
        self._subscribers.clear()
        self._global_listeners.clear()
        logger.info("AetherBusExtreme closed.")

    async def publish(self, event: AetherEvent):
        if not self._running:
            return await self.error(event, "bus_not_running")

        event = self.validate_event(event, stage="publish")
        self.ensure_correlation_id(event)
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
                        async def _wrap():
                            return res
                        tasks.append(_wrap())
            except Exception as exc:
                logger.error("Error preparing callback: %s", exc)

        if event.session_id:
            if event.session_id in self._subscribers:
                add_task(self._subscribers[event.session_id], event)
            elif event.session_id == "*":
                for callback in self._subscribers.values():
                    add_task(callback, event)

        if event.session_id is None:
            for callback in self._subscribers.values():
                add_task(callback, event)

        for listener in self._global_listeners:
            add_task(listener, event)

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            errors = [result for result in results if isinstance(result, Exception)]
            if errors:
                return await self.error(event, f"subscriber_errors={len(errors)}")
        return await self.ack(event, "compatibility_dispatch_complete")

    async def subscribe(self, session_id: str, callback: Callable[[AetherEvent], Awaitable[None]]):
        if session_id in self._subscribers:
            logger.warning("AetherBusExtreme session %s already subscribed; overwriting.", session_id)
        self._subscribers[session_id] = callback

    async def unsubscribe(self, session_id: str):
        if session_id in self._subscribers:
            del self._subscribers[session_id]

    async def add_global_listener(self, callback: Callable[[AetherEvent], Awaitable[None]]):
        self._global_listeners.add(callback)
