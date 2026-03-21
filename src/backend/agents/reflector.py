import time
import uuid
from typing import Any, Dict

from src.backend.gems.lifecycle import GemStatus
from src.backend.gems.repository import GemRepository


class Reflector:
    """Converts incidents/outcomes into reusable Gems of Wisdom."""

    def __init__(self, repository: GemRepository | None = None):
        self.repository = repository or GemRepository()

    def propose_gem(self, context: str, pattern: str, principle: str, guidance: str, confidence: float, evidence_episodes: list[str]) -> Dict[str, Any]:
        gem = {
            "gem_id": f"gem-{uuid.uuid4().hex[:10]}",
            "title": f"Lesson from {context[:40]}",
            "context": context,
            "pattern": pattern,
            "principle": principle,
            "guidance": guidance,
            "confidence": confidence,
            "evidence_episodes": evidence_episodes,
            "status": GemStatus.PROPOSED.value,
            "created_at": time.time(),
        }
        return self.repository.add(gem)
