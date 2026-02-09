import os
import logging
import asyncio
from typing import Any, Protocol, Union, Callable, Awaitable

from src.backend.genesis_core.protocol.schemas import AetherEvent

logger = logging.getLogger("BusFactory")

# Protocol Definition for AetherBus (Data Plane)
class BusInterface(Protocol):
    async def connect(self) -> None: ...
    async def close(self) -> None: ...
    async def publish(self, event: AetherEvent) -> None: ...
    async def subscribe(self, session_id: str, callback: Callable[[AetherEvent], Awaitable[None]]) -> None: ...
    async def unsubscribe(self, session_id: str) -> None: ...
    def write(self, topic: str, payload: Any) -> str: ...

class BusFactory:
    _instance = None

    @staticmethod
    def get_bus() -> BusInterface:
        """
        Polymorphic Factory: Returns the optimal Bus implementation for the current environment.
        In Web-Native mode, it defaults to AetherBusExtreme (AsyncIO).
        """
        if BusFactory._instance:
            return BusFactory._instance

        logger.info("🏭 BusFactory: Selecting AetherBusExtreme (Web-Native Mode)")
        from src.backend.genesis_core.bus.extreme import AetherBusExtreme
        BusFactory._instance = AetherBusExtreme()

        return BusFactory._instance
