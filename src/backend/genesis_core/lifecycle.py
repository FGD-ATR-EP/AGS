import asyncio
import logging
import json
import uuid
from typing import Dict, Any, Optional

from src.backend.genesis_core.bus.factory import BusFactory
from src.backend.genesis_core.agents.validator import ValidatorAgent
from src.backend.genesis_core.agents.agio_sage import AgioSage
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext
from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType

logger = logging.getLogger("LifecycleManager")

class LifecycleManager:
    """
    The Conductor of the Bio-Digital Organism.
    Manages the lifecycle of agents, the neural bus, and the heartbeat of the system.
    Transitioned to AetherBusExtreme (Web-Native).
    """
    def __init__(self):
        self.bus = BusFactory.get_bus()
        self.validator = ValidatorAgent()
        self.agio_sage = AgioSage()

        self.running = False
        self.tasks = []
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def startup(self):
        """Awakens the system."""
        logger.info("🌅 [Lifecycle] Initiating Awakening Sequence...")

        # 1. Connect Neural Bus
        await self.bus.connect()

        # Subscribe to all events for internal routing
        await self.bus.subscribe("lifecycle_manager", self._on_bus_event)

        self.running = True
        logger.info("✨ [Lifecycle] System Awakened (Web-Native). Ready to exist.")

    async def _on_bus_event(self, event: AetherEvent):
        """Routes incoming AetherEvents back to SystemIntent logic if needed."""
        if not event.extensions or "system_intent" not in event.extensions:
            return

        try:
            intent_data = event.extensions["system_intent"]
            intent = SystemIntent(**intent_data)

            # 1. Correlation Check
            if intent.correlation_id in self.pending_requests:
                future = self.pending_requests[intent.correlation_id]
                if not future.done():
                    future.set_result(intent)

            # 2. Logic Routing
            if intent.intent_type == "COGNITIVE_QUERY":
                asyncio.create_task(self._handle_cognitive_query(intent))

        except Exception as e:
            logger.error(f"Error in lifecycle bus event handler: {e}")

    async def shutdown(self):
        """Enters Nirodha (Final Sleep)."""
        logger.info("🌙 [Lifecycle] Entering Nirodha...")
        self.running = False
        for task in self.tasks:
            task.cancel()
        await self.bus.close()

    async def inject_intent(self, intent: SystemIntent) -> str:
        """
        Sopan Protocol Entry Point.
        Broadcasts intent to the AetherBus.
        """
        event = AetherEvent(
            type=AetherEventType.INTENT_DETECTED,
            session_id=None
        )
        event.extensions["system_intent"] = intent.model_dump()
        await self.bus.publish(event)
        return intent.vector_id

    async def process_request(self, intent: SystemIntent, timeout: float = 10.0) -> Optional[SystemIntent]:
        """
        Injects an intent and waits for a response via AetherBus.
        """
        future = asyncio.get_running_loop().create_future()
        self.pending_requests[intent.vector_id] = future

        try:
            await self.inject_intent(intent)
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            logger.error(f"⌛ [Lifecycle] Request {intent.vector_id} timed out.")
            # Fallback for tests or disconnected bus
            return await self.agio_sage.process_query(intent)
        finally:
            self.pending_requests.pop(intent.vector_id, None)

    async def _handle_cognitive_query(self, intent: SystemIntent):
        """
        Orchestrates the cognitive cycle: Validator -> AgioSage -> Bus
        """
        # 1. Audit Gate (Validator)
        if not self.validator.audit_gate(intent):
            logger.warning(f"🛡️ [Audit] Intent {intent.vector_id} rejected.")

            rejection_payload = IntentPayload(
                content={
                    "text_content": "[System: Intent Rejected by Patimokkha Code]",
                    "intent": {"category": "SYSTEM_OPS", "purity": 0.0},
                    "temporal_state": {"phase": "ERROR", "stability": 0.0}
                },
                modality="json"
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
            await self.inject_intent(response_intent)

    def get_status(self) -> Dict[str, Any]:
        return {
            "state": "AWAKENED" if self.running else "NIRODHA",
            "agents": ["ValidatorAgent", "AgioSage"],
            "bus": "AetherBusExtreme"
        }
