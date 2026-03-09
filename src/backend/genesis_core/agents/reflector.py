import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

logger = logging.getLogger("Reflector")

class GemOfWisdom(BaseModel):
    gem_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    title: str
    context: str
    pattern: str
    principle: str
    confidence: float
    evidence_episodes: List[str]
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "PROPOSED" # PROPOSED, ACTIVE, DEPRECATED

class Reflector:
    """
    The 'Self-Aware' Agent.
    Analyzes episodes to extract patterns and propose improvements.
    """
    def __init__(self, memory_projection):
        self.memory = memory_projection
        self.active_gems: List[GemOfWisdom] = []

    async def reflect_on_episode(self, episode_id: str, success: bool, feedback: Optional[str] = None) -> Optional[GemOfWisdom]:
        """Analyzes a specific task completion episode."""
        # In a real system, this would call AgioSage (LLM) to perform deep reflection.
        # Here we implement a heuristic pattern detector.

        logger.info(f"🤔 [Reflector] Reflecting on episode {episode_id} (Success: {success})")

        if not success:
            # Pattern: Repeated failure in specific domain
            return GemOfWisdom(
                title="Pre-action Validation Needed",
                context="Operations impacting external systems or destructive file actions",
                pattern="Actions of Tier 2+ without preview often result in user rejection or error.",
                principle="Always generate a simulation preview for high-risk actions to align intent.",
                confidence=0.8,
                evidence_episodes=[episode_id]
            )

        if feedback and "prefer" in feedback.lower():
            return GemOfWisdom(
                title="User Style Adaptation",
                context="Information presentation",
                pattern="User explicitly mentioned preference for specific format.",
                principle=f"Adjust interaction style based on feedback: {feedback}",
                confidence=0.9,
                evidence_episodes=[episode_id]
            )

        return None

    def get_active_gems(self) -> List[GemOfWisdom]:
        return [g for g in self.active_gems if g.status == "ACTIVE"]

    def adopt_gem(self, gem: GemOfWisdom):
        gem.status = "ACTIVE"
        self.active_gems.append(gem)
        logger.info(f"💎 [Reflector] Gem Adopted: {gem.title}")
