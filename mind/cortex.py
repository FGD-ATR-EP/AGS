import logging
import asyncio
from typing import Optional
from bus.event_bus import bus
from bus.intent import AetherEnvelope, create_intent
from governance.audit import audit_gate
from governance.validator import validator

logger = logging.getLogger("MindLogic")

class Cortex:
    """
    The Thinking Machine.
    Manages the Primary Cortex (LLM) and fallbacks.
    """
    def __init__(self):
        self.active_model = "Gemini-3-Pro-Stub" # Placeholder

    async def think(self, prompt: str, context: AetherEnvelope) -> str:
        """
        Processes a thought.
        """
        # 1. Audit Check (Input) - Structural/Safety
        if not audit_gate.inspira_check(context):
           return "I cannot fulfill this request as it violates the Patimokkha Code (Principle A)."

        # 2. Validator Check (Input) - Truthfulness/Consistency
        # For simplicity, we audit incoming context before thinking
        validation = await validator.audit_action(context)
        if validation["status"] == "FAILED":
             return f"Processing halted. Verification failed: {validation['reason']}"

        logger.info(f"[Cortex] Thinking with {self.active_model}...")
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        # In a real implementation, this would call the Gemini API.
        thought = f"Analysis of '{prompt}' completed by {self.active_model}. Logic follows Niyama principles."
        
        return thought

    async def wakeup(self):
        logger.info("[Cortex] Connecting to Neural Fabric...")
        bus.subscribe("USER.QUERY", self._handle_user_query)

    async def _handle_user_query(self, vector: AetherEnvelope):
        query = vector.payload.get("query", "")
        response = await self.think(query, vector)
        
        # Reply
        reply_intent = create_intent(
            type="SYSTEM.RESPONSE",
            payload={"response": response},
            context={"reply_to": vector.vector_id},
            from_agent="MIND_LOGIC"
        )
        await bus.publish("SYSTEM.RESPONSE", reply_intent)

brain = Cortex()
