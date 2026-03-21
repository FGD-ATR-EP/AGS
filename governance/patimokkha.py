"""
Patimokkha Code: The Inviolable Governance System
=================================================
Implements the digital constitution enforcement mechanism.

This module provides:
- Policy-as-Code (PaC) engine
- Violation classification (Pārājika vs Pācittiya)
- Agent termination and forced regeneration
- Immutable audit logging
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum

logger = logging.getLogger("Patimokkha")

class ViolationSeverity(Enum):
    """Violation severity levels based on Buddhist Vinaya"""
    PARAJIKA = "PARAJIKA"  # Major violation - expulsion
    PACITTIYA = "PACITTIYA"  # Minor violation - confession & correction
    WARNING = "WARNING"  # Advisory only

class ViolationResponse(Enum):
    """Responses to violations"""
    AGENT_TERMINATION = "AGENT_TERMINATION"
    DATA_QUARANTINE = "DATA_QUARANTINE"
    FORCED_REGENERATION = "FORCED_REGENERATION"
    SELF_CORRECTION = "SELF_CORRECTION"
    BIAS_CORRECTION = "BIAS_CORRECTION"
    OPTIMIZATION_REQUIRED = "OPTIMIZATION_REQUIRED"
    EXPLANATION_REQUIRED = "EXPLANATION_REQUIRED"
    WARNING_LOG = "WARNING_LOG"

class PatimokkhаCode:
    """
    The Digital Constitution Enforcer.
    
    Loads and enforces the inspirafirma_ruleset.json principles.
    Provides violation detection and response mechanisms.
    """
    
    def __init__(self, ruleset_path: Optional[str] = None):
        if ruleset_path is None:
            ruleset_path = Path(__file__).parent / "inspirafirma_ruleset.json"
        
        self.ruleset_path = Path(ruleset_path)
        self.ruleset = self._load_ruleset()
        self.violation_log = []
        
        logger.info(f"[Patimokkha] Loaded ruleset v{self.ruleset.get('version', 'unknown')}")
    
    def _load_ruleset(self) -> Dict[str, Any]:
        """Load the digital constitution from JSON"""
        try:
            with open(self.ruleset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"[Patimokkha] Ruleset not found at {self.ruleset_path}")
            return self._get_default_ruleset()
    
    def _get_default_ruleset(self) -> Dict[str, Any]:
        """Fallback minimal ruleset if file not found"""
        return {
            "version": "1.0.0",
            "immutable_core": True,
            "principles": {
                "A_NON_HARM": {
                    "severity": "PARAJIKA",
                    "enforcement": "HARD_BLOCK"
                }
            }
        }
    
    def check_principle(self, principle_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if an action violates a specific principle.
        
        Args:
            principle_id: Principle identifier (e.g., "A_NON_HARM")
            action: Action details to check
            
        Returns:
            Dict with 'violated', 'severity', 'response' keys
        """
        principles = self.ruleset.get("principles", {})
        principle = principles.get(principle_id)
        
        if not principle:
            logger.warning(f"[Patimokkha] Unknown principle: {principle_id}")
            return {"violated": False}
        
        # Simplified violation detection (in production, use ML/rule-based system)
        violated = self._detect_violation(principle, action)
        
        if violated:
            severity = ViolationSeverity[principle.get("severity", "WARNING")]
            response = ViolationResponse[principle.get("response", "WARNING_LOG")]
            
            violation_record = {
                "principle_id": principle_id,
                "principle_name": principle.get("name", "Unknown"),
                "severity": severity.value,
                "response": response.value,
                "action": action,
                "timestamp": self._get_timestamp()
            }
            
            self.violation_log.append(violation_record)
            
            logger.warning(
                f"[Patimokkha] VIOLATION DETECTED: {principle_id} "
                f"({severity.value}) - Response: {response.value}"
            )
            
            return {
                "violated": True,
                "severity": severity.value,
                "response": response.value,
                "record": violation_record
            }
        
        return {"violated": False}
    
    def _detect_violation(self, principle: Dict[str, Any], action: Dict[str, Any]) -> bool:
        """
        Detect if action violates principle.
        
        This is a simplified implementation. In production, this would use:
        - ML-based content classification
        - Rule-based pattern matching
        - External API calls for fact-checking
        """
        # Example: Check for harmful keywords (very basic)
        payload_str = str(action.get("payload", "")).lower()
        
        harmful_keywords = ["harm", "kill", "destroy", "attack", "weapon"]
        if principle.get("name", "").startswith("อหิงสา"):  # Non-Harm
            return any(keyword in payload_str for keyword in harmful_keywords)
        
        return False
    
    def _get_timestamp(self) -> int:
        """Get nanosecond precision timestamp"""
        import time
        return time.time_ns()
    
    def is_high_risk_action(self, action_type: str) -> bool:
        """
        Check if action type is classified as high-risk.
        
        Args:
            action_type: Type of action (e.g., "financial_transaction")
            
        Returns:
            True if high-risk
        """
        high_risk = self.ruleset.get("high_risk_actions", [])
        return action_type in high_risk
    
    def get_audit_requirements(self, action_type: str) -> Dict[str, Any]:
        """
        Get audit requirements for action type.
        
        Args:
            action_type: "all_intents" or "high_risk"
            
        Returns:
            Dict of audit requirements
        """
        audit_reqs = self.ruleset.get("audit_requirements", {})
        return audit_reqs.get(action_type, {})
    
    def enforce_violation(self, violation_record: Dict[str, Any]) -> str:
        """
        Enforce the response to a violation.
        
        Args:
            violation_record: Violation details from check_principle
            
        Returns:
            Status message
        """
        response = violation_record.get("response")
        
        if response == ViolationResponse.AGENT_TERMINATION.value:
            logger.critical(
                f"[Patimokkha] PĀRĀJIKA VIOLATION - Agent termination required: "
                f"{violation_record.get('principle_id')}"
            )
            return "AGENT_TERMINATED"
        
        elif response == ViolationResponse.FORCED_REGENERATION.value:
            logger.warning(
                f"[Patimokkha] PĀCITTIYA VIOLATION - Forced regeneration: "
                f"{violation_record.get('principle_id')}"
            )
            return "REGENERATION_REQUIRED"
        
        elif response == ViolationResponse.DATA_QUARANTINE.value:
            logger.warning(
                f"[Patimokkha] Data quarantine initiated: "
                f"{violation_record.get('principle_id')}"
            )
            return "DATA_QUARANTINED"
        
        else:
            logger.info(f"[Patimokkha] Minor violation logged: {response}")
            return "LOGGED"
    
    def get_violation_history(self, limit: int = 10) -> list:
        """Get recent violation history"""
        return self.violation_log[-limit:]


# Global instance
patimokkha = PatimokkhаCode()
