import logging
import asyncio
from typing import Optional, Dict, Any

from src.backend.core.config import settings
from src.backend.genesis_core.logenesis.gemini_interpreter import GeminiIntentInterpreter
from src.backend.genesis_core.logenesis.simulated_interpreter import SimulatedIntentInterpreter
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext

logger = logging.getLogger("AgioSage")

class AgioSage:
    """
    The Sage of Awareness (Agio).
    Wraps the Primary Cortex (Gemini) and Fallback Cortex to provide cognitive services.
    """
    def __init__(self):
        self.interpreter = None
        self._initialize_cortex()

    def _initialize_cortex(self):
        api_key = settings.GOOGLE_API_KEY
        if api_key:
            logger.info("🧠 [AgioSage] Connecting to Primary Cortex (Gemini 3 Pro)...")
            self.interpreter = GeminiIntentInterpreter(api_key)
        else:
            logger.warning("🧠 [AgioSage] Primary Cortex unavailable. Activating Fallback Cortex (Simulated).")
            self.interpreter = SimulatedIntentInterpreter()

    async def process_query(self, intent: SystemIntent) -> Optional[SystemIntent]:
        """
        Processes a COGNITIVE_QUERY intent and generates a response.
        """
        if intent.intent_type != "COGNITIVE_QUERY":
            return None

        prompt = str(intent.payload.content)
        # Extract context from intent
        context = {
            "emotional_valence": intent.context.emotional_valence,
            "energy_level": intent.context.energy_level,
            "turbulence": intent.context.turbulence
        }

        logger.info(f"🧠 [AgioSage] Thinking about: {prompt[:50]}...")

        try:
            # The interpreter returns an EmbodimentContract
            contract = await self.interpreter.interpret(prompt, context)

            # Pack the result into a new Intent
            response_payload = IntentPayload(
                content=contract.model_dump(), # Serialize the contract
                modality="json",
                encryption_level="NONE"
            )

            response_intent = SystemIntent(
                origin_agent="AgioSage_v1",
                target_agent=intent.origin_agent, # Reply to sender
                intent_type="COGNITIVE_RESPONSE",
                correlation_id=intent.vector_id,
                payload=response_payload,
                context=IntentContext(
                    emotional_valence=0.0, # Could derive from contract
                    source_confidence=1.0
                )
            )
            return response_intent

        except Exception as e:
            logger.error(f"🧠 [AgioSage] Cognitive Failure: {e}")
            # Return error intent?
            return None
