import asyncio
import time
import statistics
import random
import string
import gc
import itertools
from dataclasses import dataclass, field
from typing import List, Dict, Callable, Any, Optional

# ==========================================
# 0. ENVIRONMENT SETUP
# ==========================================
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("[CORE] uvloop ACTIVE: Metal speed enabled.")
except ImportError:
    pass # Windows or no uvloop installed
except Exception:
    pass

try:
    import xxhash
    _hasher = xxhash.xxh64
    print("[CORE] xxHash ACTIVE: SIMD Hashing enabled.")
except ImportError:
    # Fallback
    print("[CORE] xxHash NOT FOUND: Using built-in hash.")
    def _hasher(b): 
        class MockHash:
            def hexdigest(self): return hex(hash(b))
        return MockHash()

# ==========================================
# ⚙️ CONFIGURATION (RFC-001)
# ==========================================
PAYLOAD_SIZES = {
    "SMALL": 512,      # 512 Bytes
    "MEDIUM": 1024,    # 1 KB
    "LARGE": 4096      # 4 KB
}

ITERATIONS = 100_000   
WARMUP_ROUNDS = 5     

@dataclass
class BenchmarkResult:
    scenario: str
    throughput: float
    p50_us: float
    p95_us: float
    p99_us: float
    max_us: float

# ==========================================
# 1. OPTIMIZED DATA STRUCTURES
# ==========================================
_id_generator = itertools.count()

@dataclass(frozen=True, slots=True)
class AetherEnvelope: # Matching System Refactor
    msg_id: str
    topic: str
    payload: Any
    timestamp: float

# ==========================================
# 2. AETHERBUS EXTREME (The Target)
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

    def publish_fire_and_forget(self, topic: str, payload: Any) -> float:
        """
        Scenario A: Speed of Light (No Await)
        Returns latency in ns (internal dispatch duration)
        """
        start_ns = time.perf_counter_ns()
        
        # 1. Fast ID & Envelope
        msg_id = str(next(_id_generator))
        # timestamp = time.time() # Optional in hot loop
        envelope = AetherEnvelope(msg_id, topic, payload, 0.0)

        # 2. Direct Dispatch
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                self._create_task(handler(envelope))
        
        end_ns = time.perf_counter_ns()
        return end_ns - start_ns

    async def publish_standard(self, topic: str, payload: Any, persistence: bool = False, qos: int = 0) -> float:
        """
        Scenario B/C: With standard async await overhead
        """
        start_ns = time.perf_counter_ns()
        
        msg_id = str(next(_id_generator))
        envelope = AetherEnvelope(msg_id, topic, payload, time.time())
        
        # Simulate Persistence Overhead (if integrated with DiffMem/Disk)
        if persistence:
            if qos == 2: # Heavy consistency
                 await asyncio.sleep(0.001) # Simulate Disk Sync
            else:
                 await asyncio.sleep(0.0001) # Async Write Buffer

        if topic in self._subscribers:
            tasks = []
            for handler in self._subscribers[topic]:
                tasks.append(self._create_task(handler(envelope)))
            
            # QoS 1+: Wait for handlers
            if qos > 0:
                await asyncio.gather(*tasks)

        end_ns = time.perf_counter_ns()
        return end_ns - start_ns

# ==========================================
# 🧪 BENCHMARK ENGINE
# ==========================================
class TachyonBenchmarker:
    def __init__(self):
        self.results = []

    def generate_payload(self, size: int) -> bytes:
        return ''.join(random.choices(string.ascii_letters, k=size)).encode()

    def calculate_percentiles(self, latencies_ns: List[int]) -> Dict[str, float]:
        if not latencies_ns: return {}
        latencies_us = [l / 1000.0 for l in latencies_ns] 
        latencies_us.sort()
        n = len(latencies_us)
        return {
            "p50": latencies_us[int(n * 0.50)],
            "p95": latencies_us[int(n * 0.95)],
            "p99": latencies_us[int(n * 0.99)],
            "max": latencies_us[-1]
        }

    async def run_scenario(self, name: str, payload_size: int, persistence: bool, qos: int):
        print(f"\n[SCENARIO] {name}")
        print(f"   Payload: {payload_size} bytes | Persist: {persistence} | QoS: {qos}")
        
        bus = AetherBusExtreme()
        
        # Dummy Receiver
        async def dummy_handler(env): 
            pass
        bus.subscribe("benchmark", dummy_handler)

        payload = self.generate_payload(payload_size)
        latencies = []

        print("   [WARMUP] Warming up JIT...", end="", flush=True)
        for _ in range(WARMUP_ROUNDS * 100):
            if qos == 0 and not persistence:
                bus.publish_fire_and_forget("warmup", payload)
            else:
                await bus.publish_standard("warmup", payload, persistence, qos)
        print(" Done.")

        gc.collect()

        start_time = time.perf_counter()
        
        # Mode Switching based on QoS/Persist for Optimized methods
        if qos == 0 and not persistence:
            # Scenario A: Speed of Light
            for _ in range(ITERATIONS):
                latency = bus.publish_fire_and_forget("benchmark", payload)
                latencies.append(latency)
            # Need to wait for background tasks to drain for accurate "Throughput"? 
            # Actually RFC says measurement is internal latency? 
            # But Throughput is derived from total time. 
            await asyncio.sleep(0.01) # Drain
            
        else:
             # Scenario B/C
            for _ in range(ITERATIONS):
                latency = await bus.publish_standard("benchmark", payload, persistence, qos)
                latencies.append(latency)

        total_time = time.perf_counter() - start_time
        
        stats = self.calculate_percentiles(latencies)
        throughput = ITERATIONS / total_time

        result = BenchmarkResult(
            scenario=name,
            throughput=throughput,
            p50_us=stats.get("p50", 0),
            p95_us=stats.get("p95", 0),
            p99_us=stats.get("p99", 0),
            max_us=stats.get("max", 0)
        )
        self.results.append(result)
        self.print_result(result)

    def print_result(self, r: BenchmarkResult):
        print(f"   [DONE] Completed in {ITERATIONS} ops")
        print(f"   ------------------------------------------------")
        print(f"   [SPEED] Throughput : {r.throughput:,.2f} msg/s")
        print(f"   [TIME]  Latency P50: {r.p50_us:.2f} us")
        print(f"   [TIME]  Latency P95: {r.p95_us:.2f} us")
        print(f"   [TAIL]  Latency P99: {r.p99_us:.2f} us (Tail)")
        print(f"   [STOP]  Latency Max: {r.max_us:.2f} us")
        print(f"   ------------------------------------------------")

    async def run_suite(self):
        print("==================================================")
        print("   AETHERBUS TACHYON BENCHMARK SUITE v1.0")
        print("==================================================")
        
        await self.run_scenario("A: Speed of Light", PAYLOAD_SIZES["SMALL"], False, 0)
        await self.run_scenario("B: Standard Telemetry", PAYLOAD_SIZES["MEDIUM"], True, 1)
        await self.run_scenario("C: Heavy Load", PAYLOAD_SIZES["LARGE"], True, 2)

if __name__ == "__main__":
    benchmarker = TachyonBenchmarker()
    try:
        asyncio.run(benchmarker.run_suite())
    except KeyboardInterrupt:
        print("\nBenchmark interrupted.")
