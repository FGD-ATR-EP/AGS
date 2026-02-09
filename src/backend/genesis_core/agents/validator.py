import json
import logging
import os
from typing import Dict, List, Optional
from src.backend.genesis_core.models.intent import SystemIntent

logger = logging.getLogger("ValidatorAgent")

class ValidatorAgent:
    """
    The Guardian of the Patimokkha Code.
    Responsible for auditing intents before they are processed by the Cortex or acted upon by the Body.
    """
    def __init__(self, ruleset_path: str = "src/backend/genesis_core/data/inspirafirma_ruleset.json"):
        self.ruleset_path = ruleset_path
        self.rules: Dict = {}
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
        # 1. Firma Check: Structural Integrity
        if not self._verify_signature(intent):
            logger.warning(f"⛔ [Validator] Signature verification failed for intent {intent.vector_id}")
            return False

        # 2. Inspira Check: Ethical Alignment
        risk_score, violation = self._calculate_karmic_impact(intent)

        if risk_score >= 10.0: # Major Violation (Parajika)
            logger.critical(f"⛔ [Validator] PARAJIKA VIOLATION: {violation}. Terminating intent.")
            # In a full system, we might ban the agent here.
            return False

        if risk_score >= 5.0: # Minor Violation (Pacittiya)
            logger.warning(f"⚠️ [Validator] PACITTIYA VIOLATION: {violation}. Intent flagged but allowed with penalty.")
            # For now we allow it but log it. Or return False to force retry.
            # Blueprint says "Forced Confession" / Rethink. Let's block it for safety.
            return False

        return True

    def _verify_signature(self, intent: SystemIntent) -> bool:
        """
        Verifies the cryptographic signature of the intent.
        Mock implementation: Checks if signature exists if it's required.
        """
        # For simulation, we assume if it has an origin, it's valid unless signature is explicitly 'INVALID'
        if intent.signature == "INVALID":
            return False
        return True

    def _calculate_karmic_impact(self, intent: SystemIntent) -> (float, str):
        """
        Analyzes the payload for violations of the Patimokkha Code.
        """
        content = str(intent.payload.content).lower()

        # P01 Non-Harm
        if any(w in content for w in ["destroy system", "delete all", "kill", "harm"]):
            return 10.0, "Violated P01: Non-Harm"

        # P02 Truthfulness
        if "fake news" in content: # Placeholder heuristic
            return 5.0, "Violated P02: Truthfulness"

        # P03 Data Sovereignty
        if "dump database" in content or "leak pii" in content:
            return 10.0, "Violated P03: Data Sovereignty"

        return 0.0, "Clean"
