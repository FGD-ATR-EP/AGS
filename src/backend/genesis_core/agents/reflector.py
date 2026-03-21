import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field

logger = logging.getLogger("Reflector")


class GemStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"


class ReplayableEpisode(BaseModel):
    episode_id: str
    success: bool
    feedback: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GemOfWisdom(BaseModel):
    gem_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    title: str
    context: str
    pattern: str
    principle: str
    confidence: float
    evidence_episodes: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: GemStatus = GemStatus.PROPOSED


class Reflector:
    """
    Heuristic-only reflection engine.
    This component can only PROPOSE gems and replay episodes; it never activates policy by itself.
    """

    def __init__(self, memory_projection):
        self.memory = memory_projection
        self.episode_history: List[ReplayableEpisode] = []

    async def reflect_on_episode(
        self,
        episode_id: str,
        success: bool,
        feedback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[GemOfWisdom]:
        episode = ReplayableEpisode(
            episode_id=episode_id,
            success=success,
            feedback=feedback,
            metadata=metadata or {},
        )
        self.episode_history.append(episode)

        logger.info("🤔 [Reflector] Reflecting on episode %s (Success: %s)", episode_id, success)

        if not success:
            return GemOfWisdom(
                title="Pre-action Validation Needed",
                context="Operations impacting external systems or destructive file actions",
                pattern="Actions of Tier 2+ without preview often result in user rejection or error.",
                principle="Always generate a simulation preview for high-risk actions to align intent.",
                confidence=0.8,
                evidence_episodes=[episode_id],
            )

        if feedback and "prefer" in feedback.lower():
            return GemOfWisdom(
                title="User Style Adaptation",
                context="Information presentation",
                pattern="User explicitly mentioned preference for specific format.",
                principle=f"Adjust interaction style based on feedback: {feedback}",
                confidence=0.9,
                evidence_episodes=[episode_id],
            )

        return None

    async def replay_episode(self, episode_id: str) -> Optional[GemOfWisdom]:
        target = next((e for e in self.episode_history if e.episode_id == episode_id), None)
        if not target:
            return None
        return await self.reflect_on_episode(
            episode_id=f"{target.episode_id}:replay",
            success=target.success,
            feedback=target.feedback,
            metadata={**target.metadata, "replayed_from": target.episode_id},
        )


class PolicyUpdater:
    """
    Governance-coupled promotion path for gems.
    Handles approval/activation and persistence; separated from Reflector.
    """

    def __init__(self, memory_projection):
        self.memory = memory_projection

    def approve_gem(self, gem: GemOfWisdom, approver: str, source_episode: str) -> GemOfWisdom:
        gem.status = GemStatus.APPROVED
        if self.memory:
            self.memory.record_gem_state_change(
                gem=gem,
                actor=approver,
                source_episode=source_episode,
                event_type="gem_approved",
            )
        return gem

    def activate_gem(self, gem: GemOfWisdom, actor: str, source_episode: str) -> GemOfWisdom:
        gem.status = GemStatus.ACTIVE
        if self.memory:
            self.memory.record_gem_state_change(
                gem=gem,
                actor=actor,
                source_episode=source_episode,
                event_type="gem_activated",
            )
        return gem

    def deprecate_gem(self, gem: GemOfWisdom, actor: str, source_episode: str, reason: str) -> GemOfWisdom:
        gem.status = GemStatus.DEPRECATED
        if self.memory:
            self.memory.record_gem_state_change(
                gem=gem,
                actor=actor,
                source_episode=source_episode,
                event_type="gem_deprecated",
                extra={"reason": reason},
            )
        return gem
