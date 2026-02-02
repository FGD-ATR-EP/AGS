import asyncio
import logging
import json
import uuid
from typing import Dict, Any, Optional

from src.backend.genesis_core.bus.hyper_sonic import HyperSonicBus, HyperSonicReader
from src.backend.genesis_core.agents.validator import ValidatorAgent
from src.backend.genesis_core.agents.agio_sage import AgioSage
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext

logger = logging.getLogger("LifecycleManager")

class LifecycleManager:
    """
    The Conductor of the Bio-Digital Organism.
    Manages the lifecycle of agents, the neural bus, and the heartbeat of the system.
    Simulates a K3s orchestration layer within a single process.
    """
    def __init__(self):
        self.bus_writer = HyperSonicBus()
        self.bus_reader = HyperSonicReader()
        self.validator = ValidatorAgent()
        self.agio_sage = AgioSage()

        self.running = False
        self.tasks = []
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def startup(self):
        """Awakens the system."""
        logger.info("🌅 [Lifecycle] Initiating Awakening Sequence...")

        # 1. Connect Neural Bus
        if not self.bus_reader.connect():
             logger.warning("⚠️ [Lifecycle] Bus Reader could not connect immediately. Retrying...")
             # In a real scenario we might wait or fail. The writer is self, so it should be fine.
             pass

        self.running = True

        # 2. Start Conductor Loop (The Heartbeat)
        self.tasks.append(asyncio.create_task(self._conductor_loop()))

        logger.info("✨ [Lifecycle] System Awakened. Ready to exist.")

    async def shutdown(self):
        """Enters Nirodha (Final Sleep)."""
        logger.info("🌙 [Lifecycle] Entering Nirodha...")
        self.running = False
        for task in self.tasks:
            task.cancel()
        self.bus_writer.close()
        self.bus_reader.close()

    async def inject_intent(self, intent: SystemIntent) -> str:
        """
        Sopan Protocol Entry Point (Devordota).
        Injects an intent into the AetherBus.
        Returns the Message ID.
        """
        # Serialize Intent
        payload_bytes = intent.model_dump_json().encode('utf-8')

        # Write to Bus
        msg_id = self.bus_writer.write(topic=intent.intent_type, payload=payload_bytes)
        return msg_id

    async def process_request(self, intent: SystemIntent, timeout: float = 10.0) -> Optional[SystemIntent]:
        """
        Injects an intent and waits for a response via AetherBus.
        Used by the API Gateway (LogenesisEngine Facade).
        """
        # Create Future
        future = asyncio.get_running_loop().create_future()
        self.pending_requests[intent.vector_id] = future

        try:
            # Inject
            await self.inject_intent(intent)

            # Wait
            logger.debug(f"⏳ [Lifecycle] Waiting for response to {intent.vector_id}...")
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"⌛ [Lifecycle] Request {intent.vector_id} timed out.")
            return None
        finally:
            self.pending_requests.pop(intent.vector_id, None)

    async def _conductor_loop(self):
        """
        The Main Event Loop.
        Reads from Bus -> Routes to Agents -> Writes Responses.
        """
        logger.info("💓 [Lifecycle] Heartbeat active.")
        while self.running:
            try:
                # Poll the bus
                # HyperSonic read yield generator. We iterate it until empty.
                for ts, msg_id, topic_hash, payload_bytes in self.bus_reader.read():
                    await self._route_message(msg_id, payload_bytes)

                await asyncio.sleep(0.05) # 20Hz Heartbeat (Fast enough for RAIL 50ms)
            except Exception as e:
                logger.error(f"💔 [Lifecycle] Arrhythmia in Conductor Loop: {e}")
                await asyncio.sleep(1.0)

    async def _route_message(self, msg_id: uuid.UUID, payload_bytes: bytes):
        """
        Decodes and routes the message to the appropriate organ (Agent).
        """
        try:
            # Decode
            data = json.loads(payload_bytes.decode('utf-8'))
            intent = SystemIntent(**data)

            logger.debug(f"⚡ [Bus] Routing Intent: {intent.intent_type} from {intent.origin_agent}")

            # Check if this is a response to a pending request
            if intent.correlation_id in self.pending_requests:
                future = self.pending_requests[intent.correlation_id]
                if not future.done():
                    future.set_result(intent)
                # We also continue routing in case others are listening?
                # For now, Point-to-Point completion is sufficient for this logic.

            # Routing Logic
            if intent.intent_type == "COGNITIVE_QUERY":
                await self._handle_cognitive_query(intent)

            # Add other handlers here (e.g. MANIFESTATION)

        except Exception as e:
            logger.error(f"⚠️ [Bus] Failed to route message {msg_id}: {e}")

    async def _handle_cognitive_query(self, intent: SystemIntent):
        """
        Orchestrates the cognitive cycle: Validator -> AgioSage -> Bus
        """
        # 1. Audit Gate (Validator)
        if not self.validator.audit_gate(intent):
            logger.warning(f"🛡️ [Audit] Intent {intent.vector_id} rejected by Validator.")

            # Send Rejection Response
            rejection_payload = IntentPayload(
                content={
                    "text_content": "[System: Intent Rejected by Patimokkha Code]",
                    "intent": {"category": "SYSTEM_OPS", "purity": 0.0},
                    "temporal_state": {"phase": "ERROR", "stability": 0.0},
                    "cognitive": {"effort": 0.0, "uncertainty": 0.0}
                },
                modality="json",
                encryption_level="NONE"
            )

            rejection_intent = SystemIntent(
                origin_agent="ValidatorAgent",
                target_agent=intent.origin_agent,
                intent_type="COGNITIVE_RESPONSE",
                correlation_id=intent.vector_id,
                payload=rejection_payload,
                context=IntentContext()
            )
            await self.inject_intent(rejection_intent)
            return

        # 2. Cognitive Processing (AgioSage)
        response_intent = await self.agio_sage.process_query(intent)

        if response_intent:
            # 3. Write Response to Bus
            await self.inject_intent(response_intent)

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": "AWAKENED" if self.running else "NIRODHA",
            "agents": ["ValidatorAgent", "AgioSage"],
            "bus": "HyperSonic"
        }
