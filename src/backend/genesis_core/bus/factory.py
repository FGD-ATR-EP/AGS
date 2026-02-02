import os
import logging
import asyncio
from typing import Any, Protocol, Union

logger = logging.getLogger("BusFactory")

from typing import Callable, Awaitable
from src.backend.genesis_core.data_structures.envelope import AkashicEnvelope

# Protocol Definition for Duck Typing
class BusInterface(Protocol):
    def write(self, topic: str, payload: Any) -> str: ...
    async def connect(self) -> None: ...
    async def close(self) -> None: ...
    async def subscribe(self, topic: str, callback: Callable[[AkashicEnvelope], Awaitable[None]]) -> None: ...

class BusFactory:
    _instance = None

    @staticmethod
    def get_bus() -> BusInterface:
        """
        Polymorphic Factory: Returns the optimal Bus implementation for the current environment.
        """
        if BusFactory._instance:
            return BusFactory._instance

        # 1. Check for Mobile Environment
        # Usually KIVY_BUILD or ANDROID_ARGUMENT
        is_android = 'ANDROID_ARGUMENT' in os.environ

        # 2. Check for Server Capabilities
        has_server_deps = False
        try:
            import uvloop
            import nats
            has_server_deps = True
        except ImportError:
            has_server_deps = False

        # Decision Logic
        if not is_android and has_server_deps:
            logger.info("🏭 BusFactory: Selecting AetherBusExtreme (Server Mode)")
            from src.backend.genesis_core.bus.extreme import AetherBusExtreme
            BusFactory._instance = AetherBusExtreme()
        else:
            mode = "Android" if is_android else "Legacy/Local"
            logger.info(f"🏭 BusFactory: Selecting HyperSonicBus ({mode} Mode)")
            from src.backend.genesis_core.bus.hyper_sonic import HyperSonicBus, HyperSonicReader
            BusFactory._instance = HyperSonicBusWrapper(HyperSonicBus(), HyperSonicReader())

        return BusFactory._instance

class HyperSonicBusWrapper:
    """Wraps HyperSonicBus to match AetherBusExtreme interface (Async connect)."""
    def __init__(self, bus, reader):
        self.bus = bus
        self.reader = reader
        self._polling_task = None
        self._subscribers = [] # List of (topic_hash, callback)

    def write(self, topic: str, payload: Any) -> str:
        # HyperSonic expects bytes. If payload is not bytes, we serialize?
        # AetherBusExtreme handles serialization inside.
        # HyperSonicBus.write expects 'bytes' payload.
        if not isinstance(payload, bytes):
            import json
            # Fallback serialization for legacy
            try:
                 payload = json.dumps(payload).encode()
            except:
                 payload = str(payload).encode()

        return self.bus.write(topic, payload)

    async def connect(self):
        # Connect reader
        self.reader.connect()
        # Start polling loop for subscribers
        if not self._polling_task:
            self._polling_task = asyncio.create_task(self._poll_loop())

    async def close(self):
        self.bus.close()
        self.reader.close()
        if self._polling_task:
            self._polling_task.cancel()

    async def subscribe(self, topic: str, callback: Callable[[AkashicEnvelope], Awaitable[None]]) -> None:
        import zlib
        topic_hash = zlib.crc32(topic.encode()) & 0xFFFFFFFF
        self._subscribers.append((topic_hash, callback))

    async def _poll_loop(self):
        import uuid
        while True:
            try:
                # Read all available messages
                for timestamp, msg_id, topic_hash, payload in self.reader.read():
                    # Check subscribers
                    for sub_hash, cb in self._subscribers:
                         # Simple hash matching (HyperSonic uses hashes)
                         # Note: HyperSonic doesn't support wildcards easily without topic string preservation.
                         # Assuming exact match for now or handled by caller logic?
                         # Actually HyperSonic drops topic string, only keeps hash.
                         # So we can only match hash.
                         if sub_hash == topic_hash:
                             # Convert to AkashicEnvelope
                             # Note: HyperSonic payload is raw bytes.
                             # AkashicEnvelope expects structure?
                             # Or we just wrap the payload.
                             envelope = AkashicEnvelope(
                                 id=msg_id.hex,
                                 timestamp=timestamp,
                                 source="unknown",
                                 target="*",
                                 topic="hash:" + str(topic_hash),
                                 payload=payload,
                                 _hash_cache=None
                             )
                             try:
                                await cb(envelope)
                             except Exception as e:
                                logger.error(f"Callback error: {e}")

                await asyncio.sleep(0.01) # Poll interval
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"HyperSonic Polling Error: {e}")
                await asyncio.sleep(1)
