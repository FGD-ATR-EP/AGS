import asyncio
import time
import logging
import sys
import os

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.genesis_core.bus.extreme import AetherBusExtreme

# Mock NATS for benchmark if no server
from unittest.mock import MagicMock, AsyncMock

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Benchmark")

async def benchmark():
    # Force use of AetherBusExtreme logic with Mock NATS to test CPU overhead

    # 1. Setup Mock NATS
    mock_nc = AsyncMock()
    mock_js = AsyncMock()

    # Mock publish_async (if used)
    f = asyncio.Future()
    f.set_result(True)
    mock_js.publish_async.return_value = f

    # Mock publish (for batch gathering)
    async def mock_publish(*args, **kwargs):
        return True
    mock_js.publish = mock_publish # Direct async func

    # In my implementation I used:
    # futures = [self.js.publish(t, d) for t, d in current_batch]
    # await asyncio.gather(*futures)
    # So self.js.publish needs to return an Awaitable.

    bus = AetherBusExtreme()
    # Bypass connect
    bus.nc = mock_nc
    bus.js = mock_js
    bus.running = True

    # Start worker manually since we mocked connect
    worker = asyncio.create_task(bus._publisher_worker())
    bus.workers.add(worker)

    logger.info("🔥 Starting AetherBusExtreme Benchmark (Mocked NATS)...")

    count = 100000
    start = time.time()

    for i in range(count):
        # Fire and forget
        await bus.publish_nowait("bench.test", {"data": i, "ts": time.time()})

    # Wait for queue to drain
    while not bus.publish_queue.empty():
        await asyncio.sleep(0.001)

    end = time.time()
    duration = end - start
    rate = count / duration

    logger.info(f"✅ Processed {count} messages in {duration:.4f}s")
    logger.info(f"🚀 Throughput: {rate:.2f} req/s")

    await bus.close()

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
        logger.info("Uvloop enabled")
    except ImportError:
        logger.info("Uvloop NOT enabled")
        pass

    asyncio.run(benchmark())
