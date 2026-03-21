import logging
import asyncio
import json
from typing import Optional, Dict, Any, Callable, Awaitable

from src.backend.core.config import settings
from src.backend.genesis_core.logenesis.gemini_interpreter import GeminiIntentInterpreter
from src.backend.genesis_core.logenesis.simulated_interpreter import SimulatedIntentInterpreter
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext as LegacyIntentContext

# New Protocol Imports
from src.backend.genesis_core.protocol.schemas import (
    AetherEvent, AetherEventType, StateData, IntentData, ManifestationData,
    IntentVector, ResonanceForm
)

logger = logging.getLogger("AgioSage")

class AgioSage:
    """
    The Sage of Awareness (Agio).
    Wraps the Primary Cortex (Gemini) and Fallback Cortex to provide cognitive services.
    Now capable of 'State Emission' via the Aetherium Protocol.
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

    async def process_query(self,
                          intent: SystemIntent,
                          emitter: Optional[Callable[[AetherEvent], Awaitable[None]]] = None
                          ) -> Optional[SystemIntent]:
        """
        Processes a COGNITIVE_QUERY intent and generates a response.
        Supports 'State Emission' via the optional `emitter` callback.
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
        session_id = intent.origin_agent if intent.origin_agent and intent.origin_agent.startswith("ae-") else None

        # --- EMISSION: Intent Detected ---
        if emitter:
            await emitter(AetherEvent(
                type=AetherEventType.INTENT_DETECTED,
                session_id=session_id,
                intent=IntentData(
                    vector=IntentVector(
                        clarity=0.9,
                        emotional_valence=intent.context.emotional_valence,
                        urgency=intent.context.energy_level,
                        trust=1.0
                    ),
                    semantic_hint="query_received",
                    raw_content=prompt
                )
            ))

            # --- EMISSION: Cognitive State (Thinking) ---
            await emitter(AetherEvent(
                type=AetherEventType.STATE_UPDATE,
                session_id=session_id,
                state=StateData(
                    state="reasoning",
                    confidence=0.3,
                    energy=0.5,
                    coherence=0.8
                )
            ))

        try:
            # The interpreter returns an EmbodimentContract
            # We treat this as the "Deep Thought" block
            contract = await self.interpreter.interpret(prompt, context)

            # --- EMISSION: Confidence Shift (Analysis Complete) ---
            if emitter:
                await emitter(AetherEvent(
                    type=AetherEventType.CONFIDENCE_SHIFT,
                    session_id=session_id,
                    state=StateData(
                        state="crystallizing",
                        confidence=0.95,
                        energy=0.2, # Calming down
                        coherence=1.0
                    )
                ))

            # --- EMISSION: Manifestation (The Result) ---
            if emitter:
                # Map contract to Manifestation
                form_map = {
                    "CHIT_CHAT": ResonanceForm.SPHERE,
                    "ANALYTIC": ResonanceForm.CUBE,
                    "CREATIVE": ResonanceForm.VORTEX,
                    "SYSTEM_OPS": ResonanceForm.GRID
                }
                intent_cat = contract.intent.category if hasattr(contract, 'intent') else "CHIT_CHAT"
                form = form_map.get(intent_cat, ResonanceForm.NEBULA)

                await emitter(AetherEvent(
                    type=AetherEventType.MANIFESTATION,
                    session_id=session_id,
                    manifestation=ManifestationData(
                        intent=intent_cat.lower(),
                        resonance=contract.temporal_state.stability,
                        form=form,
                        color="#06b6d4", # Default cyan, logic could refine this
                        content=contract.text_content
                    )
                ))

            # Pack the result into a new Intent (Legacy Output)
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
                context=LegacyIntentContext(
                    emotional_valence=0.0, # Could derive from contract
                    source_confidence=1.0
                )
            )
            return response_intent

        except Exception as e:
            logger.error(f"🧠 [AgioSage] Cognitive Failure: {e}")
            if emitter:
                await emitter(AetherEvent(
                    type=AetherEventType.DEGRADATION,
                    session_id=session_id,
                    error=str(e)
                ))
            return None
