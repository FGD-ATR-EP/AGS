from enum import IntEnum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger("GovernanceCore")

class ActionTier(IntEnum):
    TIER_0_READ_ONLY = 0
    TIER_1_REVERSIBLE_LOW_RISK = 1
    TIER_2_EXTERNAL_IMPACT = 2
    TIER_3_SENSITIVE_IRREVERSIBLE = 3

class ApprovalRequest(BaseModel):
    request_id: str
    tier: ActionTier
    actor: str
    intent_id: str
    action_type: str
    preview_data: Dict[str, Any]
    status: str = "PENDING" # PENDING, APPROVED, REJECTED

class GovernanceCore:
    """
    The heart of digital ethics and safety.
    Enforces 'What is Allowed' vs 'What is Possible'.
    """
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.pending_approvals: Dict[str, ApprovalRequest] = {}

    def assess_risk(self, action_type: str, payload: Dict) -> ActionTier:
        """Determines the risk tier of a given action."""
        # Heuristic mapping
        read_keywords = ["read", "get", "list", "view", "analyze"]
        write_keywords = ["create", "update", "edit", "patch"]
        impact_keywords = ["send", "post", "publish", "notify"]
        critical_keywords = ["delete", "remove", "erase", "format", "config_system", "payment", "withdraw"]

        action_lower = action_type.lower()

        if any(k in action_lower for k in critical_keywords):
            return ActionTier.TIER_3_SENSITIVE_IRREVERSIBLE
        if any(k in action_lower for k in impact_keywords):
            return ActionTier.TIER_2_EXTERNAL_IMPACT
        if any(k in action_lower for k in write_keywords):
            return ActionTier.TIER_1_REVERSIBLE_LOW_RISK

        return ActionTier.TIER_0_READ_ONLY

    def request_approval(self, request: ApprovalRequest) -> bool:
        """
        Registers an approval request.
        Returns True if auto-approved, False if gating is required.
        """
        if request.tier <= ActionTier.TIER_0_READ_ONLY:
            return True

        if request.tier == ActionTier.TIER_1_REVERSIBLE_LOW_RISK:
            if self.config.get("auto_approve_tier_1", True):
                return True

        self.pending_approvals[request.request_id] = request
        logger.info(f"⚖️ [Governance] Approval Required for {request.action_type} (Tier {request.tier})")
        return False

    def handle_approval(self, request_id: str, decision: str) -> bool:
        """Handles human decision for a pending request."""
        if request_id not in self.pending_approvals:
            return False

        req = self.pending_approvals[request_id]
        if decision.upper() == "APPROVED":
            req.status = "APPROVED"
            return True
        else:
            req.status = "REJECTED"
            return False
