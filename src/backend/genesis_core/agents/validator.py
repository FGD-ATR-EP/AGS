import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Tuple
from src.backend.genesis_core.models.intent import SystemIntent
from src.backend.genesis_core.governance.core import GovernanceCore, ActionTier, ApprovalRequest

logger = logging.getLogger("ValidatorAgent")

class ValidatorAgent:
    """
    The Guardian of the Patimokkha Code.
    Enhanced with GovernanceCore and Risk Tiering.
    """
    def __init__(self,
                 ruleset_path: str = "src/backend/genesis_core/data/inspirafirma_ruleset.json",
                 governance: Optional[GovernanceCore] = None):
        self.ruleset_path = ruleset_path
        self.rules: Dict = {}
        self.governance = governance or GovernanceCore()
        self.load_rules()

    def load_rules(self):
        """Loads the inviolable governance rules from disk."""
        if not os.path.exists(self.ruleset_path):
            logger.error(f"Ruleset not found at {self.ruleset_path}. Enforcing default strict mode.")
            self.rules = {"principles": []}
            return

        try:
            with open(self.ruleset_path, 'r') as f:
                self.rules = json.load(f)
            logger.info("Patimokkha Code loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load ruleset: {e}")

    def audit_gate(self, intent: SystemIntent) -> bool:
        """
        The Checkpoint.
        Returns True if the intent is allowed, False otherwise.
        """
        # 1. Signature Check
        if not self._verify_signature(intent):
            logger.warning(f"⛔ [Validator] Signature verification failed for intent {intent.vector_id}")
            return False

        # 2. Ethical Alignment (Karmic Impact)
        risk_score, violation = self._calculate_karmic_impact(intent)
        if risk_score >= 10.0:
            logger.critical(f"⛔ [Validator] PARAJIKA VIOLATION: {violation}.")
            return False
        if risk_score >= 5.0:
            logger.warning(f"⚠️ [Validator] PACITTIYA VIOLATION: {violation}.")
            return False

        # 3. Governance Approval Gate
        # Only check actions that are marked as 'EXECUTION'
        if intent.intent_type == "EXECUTION_REQUEST":
            action_type = intent.payload.content.get("action") if isinstance(intent.payload.content, dict) else "unknown"
            tier = self.governance.assess_risk(action_type, intent.payload.content)

            request = ApprovalRequest(
                request_id=str(uuid.uuid4()),
                tier=tier,
                actor=intent.origin_agent,
                intent_id=intent.vector_id,
                action_type=action_type,
                preview_data=intent.payload.content
            )

            if not self.governance.request_approval(request):
                logger.info(f"⏸️ [Validator] Intent {intent.vector_id} gated by Governance (Tier {tier}).")
                return False

        return True

    def _verify_signature(self, intent: SystemIntent) -> bool:
        if intent.signature == "INVALID":
            return False
        return True

    def _calculate_karmic_impact(self, intent: SystemIntent) -> Tuple[float, str]:
        content = str(intent.payload.content).lower()
        if any(w in content for w in ["destroy system", "delete all", "kill", "harm"]):
            return 10.0, "Violated P01: Non-Harm"
        if "fake news" in content:
            return 5.0, "Violated P02: Truthfulness"
        if "dump database" in content or "leak pii" in content:
            return 10.0, "Violated P03: Data Sovereignty"
        return 0.0, "Clean"
