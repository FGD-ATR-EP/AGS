import asyncio
import logging
from typing import Callable, List, Dict, Set
from ..models.foundation import IntentVector, IntentType
from .factory import BusFactory

# ตั้งค่า Logging ให้ดูขลังแบบ System Logs
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] AETHERIUM::%(name)s >> %(message)s')
logger = logging.getLogger("AetherBus")

class AetherBus:
    """
    Legacy compatibility wrapper for intent routing on top of the configured bus runtime.
    Deprecated as a primary runtime entrypoint; retain only for protocol compatibility.
    """
    def __init__(self):
        self._bus = BusFactory.get_bus()
        self._running = False

    def subscribe(self, intent_type: IntentType, callback: Callable):
        """ลงทะเบียน Agent เพื่อรับฟังเจตจำนงเฉพาะประเภท"""
        async def _wrapper(event):
            # Simulation unwrap
            import inspect
            from src.backend.genesis_core.protocol.schemas import AetherEvent

            payload = event
            if isinstance(event, AetherEvent):
                if event.session_id and event.session_id != str(intent_type.value) and event.session_id != "*":
                    return

                if "intent_vector" in event.extensions:
                    data = event.extensions["intent_vector"]
                    from ..models.foundation import IntentVector
                    payload = IntentVector(**data)
                elif "raw_payload" in event.extensions:
                    payload = event.extensions["raw_payload"]

            if inspect.iscoroutinefunction(callback):
                await callback(payload)
            else:
                callback(payload)

        asyncio.create_task(self._bus.subscribe(str(intent_type.value), _wrapper))
        logger.info(f"Compatibility subscription registered for signal: {intent_type.value}")

    async def publish(self, intent: IntentVector):
        """ส่งเจตจำนงเข้าสู่ระบบ"""
        from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType

        # Prepare payload
        if hasattr(intent, "model_dump"):
            intent_dict = intent.model_dump()
        elif hasattr(intent, "__dict__"):
            import dataclasses
            if dataclasses.is_dataclass(intent):
                intent_dict = dataclasses.asdict(intent)
            else:
                intent_dict = intent.__dict__
        else:
            intent_dict = str(intent)

        event = AetherEvent(
            type=AetherEventType.INTENT_DETECTED,
            session_id=str(intent.intent_type.value)
        )
        event.extensions["intent_vector"] = intent_dict
        await self._bus.publish(event)

    async def start(self):
        """เริ่มระบบประสาท"""
        self._running = True
        await self._bus.connect()
        logger.info("AetherBus kernel compatibility bridge started.")

    async def stop(self):
        """ดับระบบ (Nirodha)"""
        self._running = False
        await self._bus.close()
        logger.info("AetherBus kernel compatibility bridge stopped.")
