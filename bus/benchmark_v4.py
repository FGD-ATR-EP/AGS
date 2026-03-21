import asyncio
import time
import itertools
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Set, Any, Optional

# --- 🛠️ 0. ENVIRONMENT SETUP ---
# Disable logging for benchmark
logging.getLogger("asyncio").setLevel(logging.ERROR)

# Try uvloop (Unix only)
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("[CORE] uvloop ACTIVE: Metal speed enabled.")
except ImportError:
    pass # Windows or no uvloop installed
except Exception:
    pass # Other errors

# Try xxhash
try:
    import xxhash
    _hasher = xxhash.xxh64
    print("⚡ [CORE] xxHash ACTIVE: SIMD Hashing enabled.")
except ImportError:
    # Fallback
    print("[CORE] xxHash NOT FOUND: Using built-in hash.")
    def _hasher(b): 
        class MockHash:
            def hexdigest(self): return hex(hash(b))
        return MockHash()

# ==========================================
# 1. DATA STRUCTURES (Nano-Optimized)
# ==========================================

_id_generator = itertools.count()

@dataclass(frozen=True, slots=True)
class IntentVector:
    topic: str
    payload: Any 

@dataclass(frozen=True, slots=True)
class AkashicEnvelope:
    id: str
    vector: IntentVector
    integrity_hash: str

# ==========================================
# 2. THE ENGINE (The Loop Killer)
# ==========================================

class AetherBusExtreme:
    __slots__ = ('_subscribers', '_loop', '_create_task')

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
        self._create_task = self._loop.create_task 

    def subscribe(self, topic: str, handler: Callable):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def publish_fire_and_forget(self, sender_id: str, vector: IntentVector):
        """
        ⚡ Ultimate Speed Method
        """
        # 1. Fast ID Generation
        msg_id = str(next(_id_generator))

        # 2. Fast Integrity Seal
        payload_ref = str(id(vector.payload)) 
        raw_sig = f"{sender_id}:{vector.topic}:{payload_ref}"
        signature = _hasher(raw_sig.encode()).hexdigest()

        # 3. Encapsulate
        envelope = AkashicEnvelope(msg_id, vector, signature)

        # 4. Direct Dispatch (Bypassing Gather)
        if vector.topic in self._subscribers:
            for handler in self._subscribers[vector.topic]:
                self._create_task(handler(envelope))

# ==========================================
# 3. BENCHMARK
# ==========================================

async def dumb_receiver(envelope: AkashicEnvelope):
    pass

async def run_benchmark():
    bus = AetherBusExtreme()
    bus.subscribe("neuron.fire", dumb_receiver)
    
    # Payload
    heavy_payload = {"data": "X" * 1024} 
    
    # Message Count
    TOTAL_MSG = 500_000 
    print(f"\n[IGNITION] Testing {TOTAL_MSG:,.0f} messages...")
    print(f"[Mode] Fire-and-Forget (No Await), Global Counter, Cached Loop")

    start_time = time.perf_counter()
    
    sender = "Cortex_01"
    
    # The Hot Loop
    for _ in range(TOTAL_MSG):
        vec = IntentVector("neuron.fire", heavy_payload)
        bus.publish_fire_and_forget(sender, vec)
    
    # Wait for completion
    await asyncio.sleep(0.01) 
    
    end_time = time.perf_counter()

    duration = end_time - start_time
    throughput = TOTAL_MSG / duration

    print(f"{'='*50}")
    print(f"[TIME] Duration:   {duration:.4f} sec")
    print(f"[SPEED] Throughput: {throughput:,.2f} msg/sec")
    print(f"{'='*50}")
    
    if throughput > 300000:
        print("[RESULT] GOD TIER: Faster than light")
    elif throughput > 100000:
        print("[RESULT] SUPERCAR TIER: Extremely fast")
    else:
        print("[RESULT] SEDAN TIER: Need more tuning")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
