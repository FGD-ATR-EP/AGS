import asyncio
import uuid
import random
import sys
import os

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.backend.genesis_core.models.foundation import IntentVector, IntentType
from src.backend.genesis_core.bus.kernel import AetherBus, logger

# --- Agent จำลอง (Simulated Agents) ---

async def agio_sage_cortex(intent: IntentVector):
    """
    AgioSage: Agent ผู้ใช้เหตุผล (Cognitive Agent)
    จำลองการคิดวิเคราะห์ (Reasoning)
    """
    logger.info(f"[Inspira] AgioSage received: {intent.vector_id}")

    # จำลอง Latency ของการคิด (Deep Thinking)
    think_time = random.uniform(0.05, 0.2) # 50ms - 200ms
    await asyncio.sleep(think_time)

    logger.info(f"[Inspira] AgioSage finished reasoning regarding: {intent.payload.get('query')}")

async def validator_gate(intent: IntentVector):
    """
    Audit Gate: ผู้ตรวจสอบความปลอดภัยตามกฎ Patimokkha
    """
    # จำลองการตรวจสอบ Fast Path
    if intent.entropy > 0.8:
        logger.warning(f"[Firma] High Entropy detected! Blocking intent {intent.vector_id}")
    else:
        logger.info(f"[Firma] Intent {intent.vector_id} verified. Safe to proceed.")

# --- Lifecycle Manager ---

async def awakening_ritual():
    """พิธีกรรมการตื่นรู้ (Main Entry Point)"""
    logger.info("Initiating GENESIS Protocol...")

    # 1. Initialize Infrastructure
    bus = AetherBus()

    # 2. Connect Synapses (Wiring Agents)
    bus.subscribe(IntentType.COGNITIVE_QUERY, validator_gate) # ตรวจสอบก่อน
    bus.subscribe(IntentType.COGNITIVE_QUERY, agio_sage_cortex) # แล้วค่อยคิด

    # 3. Start System
    await bus.start()

    # 4. Simulation Loop (ส่งข้อมูลเข้ามาทดสอบ)
    logger.info("--- System Awake. Listening for Intent... ---")

    # จำลอง User Input เข้ามา 5 รายการ
    for i in range(1, 6):
        vector = IntentVector(
            vector_id=str(uuid.uuid4())[:8],
            origin_agent="UserInterface",
            intent_type=IntentType.COGNITIVE_QUERY,
            payload={"query": f"Meaning of life attempt #{i}"},
            context={"turbulence": random.random()} # สุ่มค่าความปั่นป่วน
        )
        logger.info(f"Injecting Intent: {vector.vector_id}")
        await bus.publish(vector)
        await asyncio.sleep(0.5) # จำลองจังหวะการพิมพ์ของมนุษย์

    # 5. Shutdown
    await asyncio.sleep(2) # รอให้ประมวลผลเสร็จ
    await bus.stop()
    logger.info("System Shutdown Complete.")

if __name__ == "__main__":
    try:
        # ใช้ uvloop ถ้ามี (ตาม Blueprint) แต่ Fallback เป็น asyncio ปกติ
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            logger.info("Accelerator: uvloop ACTIVE")
        except ImportError:
            logger.warning("Accelerator: uvloop NOT FOUND (Running in Standard Mode)")

        asyncio.run(awakening_ritual())
    except KeyboardInterrupt:
        pass
