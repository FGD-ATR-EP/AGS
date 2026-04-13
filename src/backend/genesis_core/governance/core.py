from enum import IntEnum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import logging
import time
from src.backend.genesis_core.protocol.schemas import AetherEvent

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
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED


class GovernanceCore:
    """
    The heart of digital ethics and safety.
    Enforces 'What is Allowed' vs 'What is Possible'.
    """

    def __init__(self, config: Optional[Dict] = None, ledger=None):
        self.config = config or {}
        self.ledger = ledger
        self.pending_approvals: Dict[str, ApprovalRequest] = {}

    def assess_risk(self, action_type: str, payload: Dict) -> ActionTier:
        """Determines the risk tier of a given action."""
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

    def validate_envelope(self, envelope: AetherEvent) -> AetherEvent:
        validated = AetherEvent.model_validate(envelope.model_dump(mode="json"))
        validated.governance.validated = True
        if not validated.correlation_id:
            raise ValueError("Governance gate requires correlation_id")
        return validated

    def _record_ledger_event(self, event_type: str, request: ApprovalRequest, decision: Optional[str] = None):
        if not self.ledger:
            return
        payload = {
            "type": event_type,
            "request_id": request.request_id,
            "tier": int(request.tier),
            "status": request.status,
            "decision": decision,
            "action_type": request.action_type,
            "preview": request.preview_data,
            "timestamp": time.time(),
        }
        self.ledger.append_record(
            payload=payload,
            actor=request.actor,
            intent_id=request.intent_id,
            causal_link=request.request_id,
        )

    def request_approval(self, request: ApprovalRequest) -> bool:
        if request.tier <= ActionTier.TIER_0_READ_ONLY:
            return True

        if request.tier == ActionTier.TIER_1_REVERSIBLE_LOW_RISK and self.config.get("auto_approve_tier_1", True):
            return True

        self.pending_approvals[request.request_id] = request
        self._record_ledger_event("approval_requested", request)
        logger.info("⚖️ [Governance] Approval Required for %s (Tier %s)", request.action_type, request.tier)
        return False

    def handle_approval(self, request_id: str, decision: str) -> bool:
        """Apply an approval decision.

        Returns ``False`` only when the request id does not exist.
        A valid REJECTED decision is still a successful governance outcome.
        """
        if request_id not in self.pending_approvals:
            return False

        req = self.pending_approvals[request_id]
        if decision.upper() == "APPROVED":
            req.status = "APPROVED"
            self._record_ledger_event("approval_decided", req, decision="APPROVED")
            return True

        req.status = "REJECTED"
        self._record_ledger_event("approval_decided", req, decision="REJECTED")
        return True

    def simulate_rule_promotion(self, gem: Dict[str, Any], shadow_mode: bool = True) -> Dict[str, Any]:
        promoted_rule = {
            "rule_id": f"rule-{gem.get('gem_id', 'unknown')}",
            "title": gem.get("title"),
            "principle": gem.get("principle"),
            "source": "gem",
            "status": "SHADOW" if shadow_mode else "ACTIVE",
        }
        result = {
            "mode": "shadow" if shadow_mode else "active",
            "would_block_actions": ["send_email", "delete_all_data"],
            "promoted_rule": promoted_rule,
        }
        if self.ledger:
            self.ledger.append_record(
                payload={"type": "policy_simulation", "result": result},
                actor="governance",
                intent_id=promoted_rule["rule_id"],
                causal_link=gem.get("gem_id"),
            )
        return result
