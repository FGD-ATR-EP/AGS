import asyncio
import logging
from typing import Callable, List, Dict, Set
from ..models.foundation import IntentVector, IntentType

# ตั้งค่า Logging ให้ดูขลังแบบ System Logs
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] AETHERIUM::%(name)s >> %(message)s')
logger = logging.getLogger("AetherBus")

class AetherBus:
    """
    ระบบประสาทส่วนกลาง (Central Nervous System)
    ทำงานแบบ Asynchronous Event-Driven ตามสถาปัตยกรรม AetherBusExtreme
    """
    def __init__(self):
        self._queue: asyncio.Queue[IntentVector] = asyncio.Queue(maxsize=10000)
        self._subscribers: Dict[IntentType, List[Callable]] = {}
        self._running = False
        self._tasks: Set[asyncio.Task] = set()

    def subscribe(self, intent_type: IntentType, callback: Callable):
        """ลงทะเบียน Agent เพื่อรับฟังเจตจำนงเฉพาะประเภท"""
        if intent_type not in self._subscribers:
            self._subscribers[intent_type] = []
        self._subscribers[intent_type].append(callback)
        logger.info(f"Synapse connected for signal: {intent_type.value}")

    async def publish(self, intent: IntentVector):
        """ส่งเจตจำนงเข้าสู่ระบบ (Fire-and-Forget)"""
        try:
            # ใช้ put_nowait ถ้าทำได้ เพื่อความเร็วสูงสุด (Hyper-Sonic)
            self._queue.put_nowait(intent)
        except asyncio.QueueFull:
            logger.warning("Neural Overload! Dropping packet to prevent seizure.")
            # ในระบบจริงอาจจะบันทึกลง Disk หรือทำ Spillover

    async def _process_stream(self):
        """ลูปหลักในการประมวลผลกระแสข้อมูล (Stream of Consciousness)"""
        logger.info("AetherBus is now RESONATING...")
        while self._running:
            try:
                intent = await self._queue.get()

                # Routing Logic (ส่งต่อให้ Agent ที่เกี่ยวข้อง)
                if intent.intent_type in self._subscribers:
                    for callback in self._subscribers[intent.intent_type]:
                        # รัน Callback แบบ Async เพื่อไม่ให้บล็อก Bus
                        task = asyncio.create_task(callback(intent))
                        self._tasks.add(task)
                        task.add_done_callback(self._tasks.discard)

                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Synaptic Misfire: {e}")

    async def start(self):
        """เริ่มระบบประสาท"""
        self._running = True
        asyncio.create_task(self._process_stream())

    async def stop(self):
        """ดับระบบ (Nirodha)"""
        self._running = False
        logger.info("Entering NIRODHA state...")
        # รอให้ Queue ว่างก่อนปิด (Graceful Shutdown)
        if not self._queue.empty():
            await self._queue.join()
