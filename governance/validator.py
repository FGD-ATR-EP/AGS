from typing import Dict, Any
import logging
import random
from bus.event_bus import bus
from bus.intent import AetherEnvelope, create_intent

logger = logging.getLogger("Validator")

class ValidatorAgent:
    """
    The Truth Keeper.
    Enforces GEP Principle C: Truthfulness and Verification.
    """
    def __init__(self, required_score: float = 0.7):
        self.required_score = required_score

    async def audit_action(self, intent: AetherEnvelope) -> Dict[str, Any]:
        """
        Audits an intent for truthfulness.
        """
        logger.info(f"[Validator] Auditing Intent {intent.vector_id[:8]}...")
        
        # Simulation of Fact Checking (Grounding)
        trust_score = random.uniform(0.5, 0.95)
        
        if trust_score < self.required_score:
            reason = "GEP_VIOLATION_PRINCIPLE_C"
            logger.warning(f"[Validator] Intent {intent.vector_id[:8]}... FAILED Truthfulness Check (Score: {trust_score:.2f})")
            
            # Publish Error for PangenesAgent (RSI Loop)
            error_envelope = create_intent(
                type="SYSTEM.ERROR",
                payload={
                    "status": "FAILED",
                    "reason": reason,
                    "violating_score": round(trust_score, 2),
                    "intent_id": intent.vector_id,
                    "summary": str(intent.payload)[:50]
                },
                from_agent="VALIDATOR",
                to_target="PANGENES"
            )
            await bus.publish("SYSTEM.ERROR", error_envelope)
            
            return {
                "status": "FAILED",
                "reason": reason,
                "score": trust_score
            }
        
        logger.info(f"[Validator] Intent {intent.vector_id[:8]}... PASSED (Score: {trust_score:.2f})")
        return {"status": "PASS", "score": round(trust_score, 2)}

validator = ValidatorAgent()
