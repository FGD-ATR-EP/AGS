import logging
from bus.event_bus import bus, AetherEnvelope
from memory.diff_mem import diff_mem
from governance.validator import validator

logger = logging.getLogger("Pangenes")

class PangenesAgent:
    """
    The Alchemist.
    Transforms pain (Errors) into wisdom (Gems).
    """
    async def activate(self):
        bus.subscribe("SYSTEM.ERROR", self._transmute_error)

    async def _transmute_error(self, vector: AetherEnvelope):
        """
        Analyzes an error/violation and commits a Gem of Wisdom to Git.
        """
        payload = vector.payload
        logger.info(f"[Pangenes] Transmuting experience...")
        
        # 1. Analyze Verification Failure
        if payload.get("status") == "FAILED":
            reason = payload.get("reason", "UNKNOWN_ERROR")
            intent_id = payload.get("intent_id", "N/A")
            score = payload.get("violating_score", 0.0)
            
            lesson = f"PREVENTION: Intent {intent_id} failed {reason} with score {score}."
            
            # 2. Crystallize to DiffMem
            gem_content = {
                "type": "NEGATIVE_REINFORCEMENT",
                "origin": intent_id,
                "lesson": lesson,
                "timestamp": vector.timestamp
            }
            
            filename = f"gem_{vector.timestamp.replace(':', '-')}.json"
            diff_mem.commit_gem(filename, gem_content, f"RSI Update: Learned from {reason}")
            
            logger.info(f"[Pangenes] Crystallized Gem: {lesson}")

alchemist = PangenesAgent()
