import time
import sys
import os
import statistics
import uuid

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.departments.presentation.lcl import LightControlLogic
from src.backend.departments.presentation.light_schemas import LightEntity

def run_benchmark(count: int, frames: int = 100):
    print(f"\n--- Benchmarking with {count} entities for {frames} frames ---")
    lcl = LightControlLogic()

    # Spawn entities
    print("Spawning entities...")

    # Pre-generate entities dictionary
    initial_entities = {}
    for i in range(count):
        eid = str(uuid.uuid4())
        initial_entities[eid] = LightEntity(
            id=eid,
            position=(0.5, 0.5),
            velocity=(0.0, 0.0),
            energy=1.0,
            target_position=(0.8, 0.8)
        )

    # Set using the setter (which populates NumPy arrays)
    lcl.entities = initial_entities

    print(f"Entities spawned: {len(lcl.entities)}") # This calls getter, verifies count

    # Warmup
    print("Warmup...")
    for _ in range(10):
        lcl.tick(0.016)

    # Measure
    print("Measuring...")
    times = []
    start_global = time.time()

    for _ in range(frames):
        t0 = time.time()
        lcl.tick(0.016) # 60 FPS dt
        t1 = time.time()
        times.append((t1 - t0) * 1000.0) # ms

    end_global = time.time()

    avg_ms = statistics.mean(times)
    min_ms = min(times)
    max_ms = max(times)
    total_time = end_global - start_global
    tps = frames / total_time

    print(f"Results for {count} entities:")
    print(f"  Avg per tick: {avg_ms:.4f} ms")
    print(f"  Min per tick: {min_ms:.4f} ms")
    print(f"  Max per tick: {max_ms:.4f} ms")
    print(f"  TPS (Ticks/sec): {tps:.2f}")

    return avg_ms, tps

if __name__ == "__main__":
    counts = [100, 1000, 5000]
    results = {}

    for c in counts:
        avg, tps = run_benchmark(c)
        results[c] = (avg, tps)

    print("\n\n=== FINAL SUMMARY ===")
    for c, (avg, tps) in results.items():
        print(f"Count: {c:<6} | Time: {avg:>8.4f} ms | TPS: {tps:>8.2f}")
