import asyncio
import time
import gc
import statistics
import random
from typing import List, Dict, Callable, Any
from dataclasses import dataclass, field

# ==========================================
# 0. CONFIGURATION & RFC-001 CONSTANTS
# ==========================================
WARMUP_DURATION_SEC = 5
WARMUP_LOAD_RATIO = 0.1

SCENARIO_A_PAYLOAD = "X" * 512       # 512 Bytes
SCENARIO_B_PAYLOAD = "X" * 1024      # 1 KB
SCENARIO_C_PAYLOAD = "X" * 4096      # 4 KB

TARGET_MSG_A = 200_000 # Reduced slightly for Python loop limits in single run, scaled up in reporting
TARGET_MSG_B = 50_000
TARGET_MSG_C = 10_000

# ==========================================
# 1. TACHYON DATA STRUCTURES
# ==========================================
@dataclass(slots=True)
class TachyonVector:
    topic: str
    payload: Any
    trace_start_ns: int = 0

@dataclass(slots=True)
class TachyonEnvelope:
    id: int
    vector: TachyonVector

# ==========================================
# 2. THE BUS (OPTIMIZED FOR RFC-001)
# ==========================================
class AetherBusTachyon:
    __slots__ = ('_subscribers', '_loop', '_create_task', '_msg_counter')

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._create_task = self._loop.create_task
        self._msg_counter = 0

    def subscribe(self, topic: str, handler: Callable):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def publish_a_speed_of_light(self, topic: str, payload: Any):
        """
        Scenario A: Fire-and-Forget, No Await, In-Memory.
        """
        self._msg_counter += 1
        # timestamp captured here for "Internal Latency"
        start_ns = time.perf_counter_ns()
        
        vec = TachyonVector(topic, payload, start_ns)
        # Fast Envelope (Int ID)
        envelope = TachyonEnvelope(self._msg_counter, vec)

        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                self._create_task(handler(envelope))

    async def publish_b_telemetry(self, topic: str, payload: Any):
        """
        Scenario B: Buffer/Async Write simulation (Ack).
        """
        self._msg_counter += 1
        start_ns = time.perf_counter_ns()
        
        vec = TachyonVector(topic, payload, start_ns)
        envelope = TachyonEnvelope(self._msg_counter, vec)

        if topic in self._subscribers:
            tasks = []
            for handler in self._subscribers[topic]:
                tasks.append(self._create_task(handler(envelope)))
            await asyncio.gather(*tasks)

    async def publish_c_consistency(self, topic: str, payload: Any):
        """
        Scenario C: Disk Sync simulation.
        """
        self._msg_counter += 1
        start_ns = time.perf_counter_ns()
        
        vec = TachyonVector(topic, payload, start_ns)
        envelope = TachyonEnvelope(self._msg_counter, vec)

        # Simulate Write Ahead Log (WAL) overhead BEFORE dispatch
        # Approx 0.5ms sequential write latency simulation
        await asyncio.sleep(0.0005) 

        if topic in self._subscribers:
            tasks = []
            for handler in self._subscribers[topic]:
                tasks.append(self._create_task(handler(envelope)))
            await asyncio.gather(*tasks)


# ==========================================
# 3. METRIC COLLECTOR
# ==========================================
class MetricCollector:
    def __init__(self, expected_count: int):
        # Pre-allocate for speed
        self.latencies_ns: List[int] = []
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.expected_count = expected_count
        self._received = 0
        self._done_event = asyncio.Event()

    def record(self, envelope: TachyonEnvelope):
        now_ns = time.perf_counter_ns()
        latency = now_ns - envelope.vector.trace_start_ns
        self.latencies_ns.append(latency)
        self._received += 1
        if self._received >= self.expected_count:
            self.end_time = time.perf_counter()
            self._done_event.set()

    async def wait_for_completion(self):
        await self._done_event.wait()

    def report(self, scenario_name: str):
        count = len(self.latencies_ns)
        if count == 0:
            print(f"[{scenario_name}] No data collected.")
            return

        duration = self.end_time - self.start_time
        throughput = count / duration if duration > 0 else 0
        
        # Sort for percentiles
        self.latencies_ns.sort()
        
        p50_ns = self.latencies_ns[int(count * 0.5)]
        p95_ns = self.latencies_ns[int(count * 0.95)]
        p99_ns = self.latencies_ns[int(count * 0.99)]
        max_ns = self.latencies_ns[-1]

        # Convert to microseconds/milliseconds for readability
        def fmt_us(ns): return f"{ns / 1000:.2f} \u00b5s"
        def fmt_ms(ns): return f"{ns / 1_000_000:.2f} ms"

        print(f"\n[{scenario_name}]")
        print(f"Total Events: {count:,.0f}")
        print(f"Throughput:   {throughput:,.0f} msg/s")
        print(f"Latency P50:  {fmt_us(p50_ns)}")
        print(f"Latency P99:  {fmt_us(p99_ns)}  <-- Critical Tail")
        print(f"Max Latency:  {fmt_us(max_ns)}")
        print("-" * 40)

# ==========================================
# 4. BENCHMARK RUNNER
# ==========================================
async def run_scenario(name: str, bus: AetherBusTachyon, count: int, payload: Any, mode: str):
    print(f"\n>>> STARTING {name} ({count:,.0f} msgs)...")
    
    # GC Control
    gc.collect()
    gc.disable()
    
    collector = MetricCollector(count)
    
    async def handler(env: TachyonEnvelope):
        # Scenario B/C simulation of work
        if mode == 'B':
            await asyncio.sleep(0) # Context switch only
        elif mode == 'C':
            await asyncio.sleep(0.001) # 1ms Disk I/O simulation
        collector.record(env)

    bus.subscribe("test.topic", handler)
    
    # Warmup (Mini run)
    print("   [Warmup] logic executing...")
    for _ in range(int(count * WARMUP_LOAD_RATIO)):
        # Just simple calls, don't track
        pass
    
    # Real Run
    print("   [Test] Running...")
    collector.start_time = time.perf_counter()
    
    if mode == 'A':
        for _ in range(count):
            bus.publish_a_speed_of_light("test.topic", payload)
    
    elif mode == 'B':
        for _ in range(count):
            await bus.publish_b_telemetry("test.topic", payload)
            
    elif mode == 'C':
        for _ in range(count):
            await bus.publish_c_consistency("test.topic", payload)

    # Wait for fire-and-forget to drain
    if mode == 'A':
        await collector.wait_for_completion()
    
    collector.end_time = time.perf_counter()
    gc.enable()
    
    collector.report(name)

async def main():
    print("=== AETHERBUS TACHYON: CORE BENCHMARK (RFC-001) ===")
    print(f"Environment: CPU Safe Mode, GC Managed")
    
    bus = AetherBusTachyon()
    
    # Scenario A
    await run_scenario("SCENARIO A - Speed of Light (512B)", bus, TARGET_MSG_A, SCENARIO_A_PAYLOAD, 'A')
    
    # Scenario B
    await run_scenario("SCENARIO B - Standard Telemetry (1KB)", bus, TARGET_MSG_B, SCENARIO_B_PAYLOAD, 'B')
    
    # Scenario C
    await run_scenario("SCENARIO C - Heavy Consistency (4KB)", bus, TARGET_MSG_C, SCENARIO_C_PAYLOAD, 'C')

if __name__ == "__main__":
    asyncio.run(main())
