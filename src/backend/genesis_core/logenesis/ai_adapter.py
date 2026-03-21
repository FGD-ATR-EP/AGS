from abc import ABC, abstractmethod
from typing import Dict, Any
from .light_schemas import LightIntent, LightAction

class AIModelAdapter(ABC):
    @abstractmethod
    async def generate_intent(self, prompt: str, scene_state: Dict[str, Any]) -> LightIntent:
        pass

class MockAdapter(AIModelAdapter):
    """
    Mock Adapter for v1.
    Simulates LLM response without actual API calls.
    """
    async def generate_intent(self, prompt: str, scene_state: Dict[str, Any]) -> LightIntent:
        prompt = prompt.lower()

        # Simulating "Move tree cluster right to left" -> vector [-0.25, 0]
        if "move" in prompt or "ย้าย" in prompt:
             return LightIntent(
                action=LightAction.MOVE,
                target="TREE_CLUSTER_RIGHT", # Mock target
                vector=(-0.25, 0.0),
                decay=0.9
            )

        if "spawn" in prompt or "create" in prompt:
            return LightIntent(
                action=LightAction.SPAWN,
                color_hint="natural_green"
            )

        return LightIntent(action=LightAction.EMPHASIZE)
