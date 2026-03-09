from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from src.backend.genesis_core.governance.core import ActionTier

class ActionPreview(BaseModel):
    summary: str
    impact: str
    risk_tier: ActionTier
    diff: Optional[str] = None

class ExecutionVessel(ABC):
    """
    Base class for all 'Body' parts.
    Vessels possess capabilities and permissions to act on specific domains.
    """
    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain

    @abstractmethod
    async def simulate(self, action: str, params: Dict) -> ActionPreview:
        """Generates a preview of the action without executing it."""
        pass

    @abstractmethod
    async def execute(self, action: str, params: Dict) -> Dict[str, Any]:
        """Performs the actual operation."""
        pass
