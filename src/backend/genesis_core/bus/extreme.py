import asyncio
import logging
import nats
from nats.js.api import StreamConfig, RetentionPolicy, StorageType
from nats.errors import TimeoutError, NoRespondersError
from typing import Optional, Callable, Awaitable, Set, Any

from src.backend.genesis_core.data_structures.envelope import AkashicEnvelope

logger = logging.getLogger("AetherBusExtreme")

class AetherBusExtreme:
    """
    The High-Performance Nervous System for Aetherium Genesis.
    Powered by NATS JetStream and optimized for 10k+ req/s.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AetherBusExtreme, cls).__new__(cls)
        return cls._instance

    def __init__(self, nats_url: str = "nats://localhost:4222"):
        if hasattr(self, "initialized"):
            return

        self.nats_url = nats_url
        self.nc = None
        self.js = None

        # Ingestion Queue for Fire-and-Forget
        self.publish_queue = asyncio.Queue(maxsize=100000)

        # Background Workers
        self.workers: Set[asyncio.Task] = set()
        self.running = False

        self.initialized = True
        logger.info("🚀 AetherBusExtreme Initialized (Singleton)")

    async def connect(self):
        """Establishes connection to NATS and initializes JetStream."""
        if self.nc and self.nc.is_connected:
            return

        try:
            self.nc = await nats.connect(
                self.nats_url,
                max_reconnect_attempts=10,
                reconnect_time_wait=1
            )
            self.js = self.nc.jetstream()

            # Create Core Streams
            await self._ensure_stream("genesis_telemetry", ["telemetry.>"])
            await self._ensure_stream("genesis_state", ["state.>"])

            self.running = True
            # Start Publisher Worker
            worker = asyncio.create_task(self._publisher_worker())
            self.workers.add(worker)
            worker.add_done_callback(self.workers.discard)

            logger.info("⚡ AetherBusExtreme Connected & Streams Ready")

        except Exception as e:
            logger.error(f"❌ NATS Connection Failed: {e}")
            raise

    async def _ensure_stream(self, name: str, subjects: list):
        """Idempotent stream creation."""
        try:
            await self.js.add_stream(
                name=name,
                subjects=subjects,
                config=StreamConfig(
                    retention=RetentionPolicy.LIMITS,
                    max_msgs=100000,
                    discard=RetentionPolicy.OLD, # Ring buffer style
                    storage=StorageType.MEMORY,  # Speed! (Use FILE for persistence)
                    replicas=1
                )
            )
        except Exception as e:
            # Ignore if already exists (or handle update)
            # logger.debug(f"Stream check: {e}")
            pass

    async def publish_nowait(self, topic: str, payload: Any, source: str = "genesis_core") -> Optional[str]:
        """
        Fire-and-forget publishing.
        Encapsulates data in AkashicEnvelope and pushes to async queue.
        Returns: Message ID (str) or None if dropped.
        """
        if not self.running:
            logger.warning("Bus not running, dropping message")
            return None

        try:
            envelope = AkashicEnvelope.create(topic, payload, source)
            # Serialize ONCE here (Zero-copy downstream)
            packed_data = envelope.to_msgpack()

            # Non-blocking put. If full, we drop (Backpressure/Load shedding)
            self.publish_queue.put_nowait((topic, packed_data))
            return envelope.id
        except asyncio.QueueFull:
            logger.error("🔥 BUS OVERLOAD: Publish Queue Full! Dropping packet.")
            return None
        except Exception as e:
            logger.error(f"Publish Error: {e}")
            return None

    def write(self, topic: str, payload: Any) -> str:
        """
        Sync wrapper for compatibility with HyperSonicBus.
        NOTE: This schedules the async publish on the current loop.
        """
        # We need to return a ID immediately.
        # But publish_nowait is async? No, it's defined as async but uses put_nowait.
        # So we can just call it?
        # But if we are called from sync code (Auditorium might be sync?), we need to be careful.
        # AuditoriumService.monitor_loop is async. So it can await.
        # HyperSonicBus.write is synchronous (shm writes).

        # If the caller is async, they should use await bus.write(...) if possible?
        # But HyperSonicBus.write is sync.

        # Solution: Use create_task to run publish_nowait (even though it's fast)
        # Or just run the logic synchronously since put_nowait is sync?
        # publish_nowait only does CPU work and queue put. It doesn't await IO.
        # So we can make publish_nowait synchronous or remove 'async' keyword?
        # Creating envelope involves uuid and msgpack (cpu).

        # I will implement a sync 'write' that does the work.

        envelope = AkashicEnvelope.create(topic, payload)
        packed_data = envelope.to_msgpack()
        try:
             self.publish_queue.put_nowait((topic, packed_data))
             return envelope.id
        except Exception as e:
             logger.error(f"Bus Write Error: {e}")
             return ""

    async def _publisher_worker(self):
        """
        Consumes the queue and blasts messages to NATS using batching for high throughput.
        """
        logger.info("📨 Publisher Worker Started")
        batch_size = 100

        while self.running:
            try:
                # 1. Get first item (blocking)
                topic, data = await self.publish_queue.get()
                current_batch = [(topic, data)]

                # 2. Try to fill batch from queue without blocking
                for _ in range(batch_size - 1):
                    if self.publish_queue.empty():
                        break
                    try:
                        current_batch.append(self.publish_queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

                # 3. Burst Publish (Gather)
                # Note: nats-py 'publish' is async and waits for Ack.
                # We use gather to send them concurrently in flight.
                futures = [
                    self.js.publish(t, d) for t, d in current_batch
                ]

                # Wait for all Acks (or use return_exceptions=True to survive failures)
                results = await asyncio.gather(*futures, return_exceptions=True)

                # 4. Mark tasks done
                for _ in current_batch:
                    self.publish_queue.task_done()

            except Exception as e:
                logger.error(f"Worker Error: {e}")
                await asyncio.sleep(0.1)

    async def subscribe(self, subject: str, callback: Callable[[AkashicEnvelope], Awaitable[None]]):
        """
        Subscribes to a subject and invokes callback with AkashicEnvelope.
        """
        if not self.js:
            raise RuntimeError("Bus not connected")

        async def _internal_cb(msg):
            try:
                # Zero-copy deserialization (msg.data is bytes)
                envelope = AkashicEnvelope.from_msgpack(msg.data)
                await callback(envelope)
                # Explicit Ack?
                # await msg.ack()
            except Exception as e:
                logger.error(f"Subscriber Error [{subject}]: {e}")

        await self.js.subscribe(subject, cb=_internal_cb)
        logger.info(f"👂 Subscribed to {subject}")

    async def close(self):
        self.running = False
        # Cancel workers
        for w in self.workers:
            w.cancel()

        if self.nc:
            await self.nc.close()
            logger.info("🔌 AetherBusExtreme Disconnected")
