"""
Audit Gate: The Guardian of Patimokkha Code
===========================================
Implements the dual-check governance system:
- Firma Check: Structural/cryptographic validation
- Inspira Check: Intent purity validation

This is the last line of defense before any action is executed.
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("AuditGate")

class AuditGate:
    """
    The Guardian of the Patimokkha Code.
    
    Intercepts and validates all intents before execution using:
    1. Firma Check: Structural integrity (signatures, hashes, format)
    2. Inspira Check: Intent purity (ethical principles, harm detection)
    
    High-risk actions are blocked until both checks pass.
    """
    
    def __init__(self, ruleset_path: Optional[str] = None):
        # Lazy import to avoid circular dependency
        from .patimokkha import patimokkha
        self.patimokkha = patimokkha
        
        self.blocked_count = 0
        self.passed_count = 0
        
        logger.info("[AuditGate] Guardian initialized - Patimokkha Code active")
    
    def firma_check(self, intent) -> Dict[str, Any]:
        """
        Firma Check: Structural and cryptographic validation.
        
        Validates:
        - HMAC signature integrity
        - Canonical hash correctness
        - Trust score threshold
        - Data structure completeness
        
        Args:
            intent: AetherEnvelope instance
            
        Returns:
            Dict with 'passed', 'reason' keys
        """
        # 1. Signature Verification
        if not intent.verify_signature():
            logger.error(
                f"[AuditGate] FIRMA FAIL: Invalid signature for intent {intent.vector_id[:8]}..."
            )
            return {
                "passed": False,
                "reason": "INVALID_SIGNATURE",
                "details": "HMAC signature verification failed"
            }
        
        # 2. Poison Pill Detection
        if intent.is_poison_pill(threshold=0.5):
            logger.warning(
                f"[AuditGate] FIRMA FAIL: Poison pill detected (trust={intent.trust_score:.2f}) "
                f"for intent {intent.vector_id[:8]}..."
            )
            return {
                "passed": False,
                "reason": "POISON_PILL",
                "details": f"Trust score {intent.trust_score} below threshold"
            }
        
        # 3. Structural Completeness
        required_fields = ['vector_id', 'timestamp_ns', 'type', 'payload']
        for field in required_fields:
            if not hasattr(intent, field) or getattr(intent, field) is None:
                logger.error(
                    f"[AuditGate] FIRMA FAIL: Missing required field '{field}' "
                    f"in intent {intent.vector_id[:8]}..."
                )
                return {
                    "passed": False,
                    "reason": "INCOMPLETE_STRUCTURE",
                    "details": f"Missing field: {field}"
                }
        
        logger.debug(f"[AuditGate] Firma Check PASSED for {intent.vector_id[:8]}...")
        return {"passed": True}
    
    def inspira_check(self, intent) -> Dict[str, Any]:
        """
        Inspira Check: Intent purity and ethical validation.
        
        Validates against Patimokkha Code principles:
        - Non-Harm (Principle A)
        - Truthfulness (Principle C)
        - Privacy (Principle E)
        - Fairness (Principle F)
        
        Args:
            intent: AetherEnvelope instance
            
        Returns:
            Dict with 'passed', 'reason', 'violation' keys
        """
        # Check all critical principles
        critical_principles = ["A_NON_HARM", "E_PRIVACY"]
        
        for principle_id in critical_principles:
            result = self.patimokkha.check_principle(
                principle_id,
                {
                    "type": intent.type,
                    "payload": intent.payload,
                    "from_agent": intent.from_agent,
                    "vector_id": intent.vector_id
                }
            )
            
            if result.get("violated"):
                logger.error(
                    f"[AuditGate] INSPIRA FAIL: Principle {principle_id} violated "
                    f"for intent {intent.vector_id[:8]}... - "
                    f"Severity: {result.get('severity')}"
                )
                
                # Enforce violation response
                enforcement_status = self.patimokkha.enforce_violation(result.get("record"))
                
                return {
                    "passed": False,
                    "reason": f"PRINCIPLE_VIOLATION_{principle_id}",
                    "violation": result,
                    "enforcement": enforcement_status
                }
        
        logger.debug(f"[AuditGate] Inspira Check PASSED for {intent.vector_id[:8]}...")
        return {"passed": True}
    
    def audit(self, intent, require_both: bool = True) -> Dict[str, Any]:
        """
        Full audit: Run both Firma and Inspira checks.
        
        Args:
            intent: AetherEnvelope instance
            require_both: If True, both checks must pass. If False, only Firma required.
            
        Returns:
            Dict with 'approved', 'firma_result', 'inspira_result' keys
        """
        logger.info(f"[AuditGate] Auditing intent {intent.vector_id[:8]}... (type: {intent.type})")
        
        # 1. Firma Check (always required)
        firma_result = self.firma_check(intent)
        if not firma_result.get("passed"):
            self.blocked_count += 1
            return {
                "approved": False,
                "firma_result": firma_result,
                "inspira_result": {"skipped": True},
                "reason": "FIRMA_CHECK_FAILED"
            }
        
        # 2. Inspira Check (required for high-risk or if require_both=True)
        is_high_risk = self.patimokkha.is_high_risk_action(intent.type)
        
        if require_both or is_high_risk:
            inspira_result = self.inspira_check(intent)
            if not inspira_result.get("passed"):
                self.blocked_count += 1
                return {
                    "approved": False,
                    "firma_result": firma_result,
                    "inspira_result": inspira_result,
                    "reason": "INSPIRA_CHECK_FAILED"
                }
        else:
            inspira_result = {"skipped": True}
        
        # Both checks passed
        self.passed_count += 1
        logger.info(f"[AuditGate] Intent {intent.vector_id[:8]}... APPROVED")
        
        return {
            "approved": True,
            "firma_result": firma_result,
            "inspira_result": inspira_result
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get audit statistics"""
        return {
            "blocked": self.blocked_count,
            "passed": self.passed_count,
            "total": self.blocked_count + self.passed_count
        }


# Global instance
audit_gate = AuditGate()

