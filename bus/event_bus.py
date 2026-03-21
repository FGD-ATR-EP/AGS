import asyncio
import time
import itertools
import logging
import uuid
import hashlib
import json
from typing import Dict, List, Callable, Awaitable, Any, Optional
from .intent import AetherEnvelope, create_intent

# --- OPTIMIZATION SETUP ---
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

try:
    import xxhash
    _hasher = xxhash.xxh64
except ImportError:
    def _hasher(b):
        class MockHash:
            def hexdigest(self): return hashlib.sha256(b).hexdigest()
        return MockHash()

logger = logging.getLogger("AetherBus")
_id_generator = itertools.count()

class AetherBus:
    """
    The Central Nervous System (Tachyon Edition).
    v4.0: Optimized for High-Frequency Low-Latency Messaging.
    """
    __slots__ = ('_subscribers', '_loop', '_create_task', '_initialized', '_msg_counter')
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AetherBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._subscribers: Dict[str, List[Callable[[AetherEnvelope], Awaitable[None]]]] = {}
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        
        self._create_task = self._loop.create_task
        self._msg_counter = itertools.count()
        self._initialized = True
        logger.info("[AetherBus] Tachyon Engine v4.0 Initialized.")

    def subscribe(self, intent_type: str, callback: Callable[[AetherEnvelope], Awaitable[None]]):
        if intent_type not in self._subscribers:
            self._subscribers[intent_type] = []
        self._subscribers[intent_type].append(callback)
        logger.info(f"[AetherBus] Agent subscribed to '{intent_type}'")

    async def publish(self, intent_type: str, vector: AetherEnvelope, persistence: bool = False, qos: int = 0):
        """
        Publishes an AetherEnvelope to the bus.
        Supports Fire-and-Forget (QoS 0) and Awaited (QoS 1+).
        """
        # 1. Fast ID Generation (if not already set or for internal tracking)
        # Note: AetherEnvelope already has msg_id, but we can verify integrity here
        
        # 2. Dispatch
        if intent_type in self._subscribers:
            tasks = []
            for callback in self._subscribers[intent_type]:
                # Optimized Dispatch
                tasks.append(self._create_task(self._safe_execute(callback, vector)))
            
            # QoS Handling
            if qos > 0:
                await asyncio.gather(*tasks)
            else:
                # QoS 0: Fire and Forget (Already created task)
                pass
                
            # logger.debug(f"[AetherBus] Dispatched {len(tasks)} tasks via Tachyon express.")
        else:
            logger.warning(f"[AetherBus] No subscribers for '{intent_type}'")

    async def _safe_execute(self, callback, vector):
        try:
            await callback(vector)
        except Exception as e:
            logger.error(f"[AetherBus] Audit Monitor caught error in callback: {e}")

# Global Access Point
bus = AetherBus()
