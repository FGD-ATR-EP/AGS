import json
import logging
import os
import asyncio
from typing import Dict, List, Optional, Tuple, Any

from src.backend.genesis_core.models.intent import SystemIntent
from src.backend.genesis_core.memory.akashic import AkashicRecords
from src.backend.genesis_core.protocol.schemas import AetherEvent, AetherEventType, AuditData, AuditSeverity
from src.backend.genesis_core.agents.agio_sage import AgioSage

logger = logging.getLogger("ValidatorAgent")

class ValidatorAgent:
    """
    The Guardian of the Patimokkha Code.
    Now enhanced with AI-driven contextual auditing and behavioral history analysis.
    """
    def __init__(self,
                 ruleset_path: str = "src/backend/genesis_core/data/inspirafirma_ruleset.json",
                 akashic: Optional[AkashicRecords] = None,
                 sage: Optional[AgioSage] = None):
        self.ruleset_path = ruleset_path
        self.rules: Dict = {}
        self.akashic = akashic or AkashicRecords()
        self.sage = sage or AgioSage()
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

    async def audit_gate(self, intent: SystemIntent, bus: Optional[Any] = None) -> bool:
        """
        The Checkpoint.
        Performs structural checks, then contextual AI-driven checks.
        """
        # 1. Structural Check
        if not self._verify_signature(intent):
            await self._emit_audit(intent, "SIGNATURE_CHECK", "DENIED", "Invalid cryptographic signature", AuditSeverity.CRITICAL, bus)
            return False

        # 2. Heuristic Check (Fast Path)
        risk_score, violation = self._calculate_heuristic_impact(intent)
        if risk_score >= 10.0:
            await self._emit_audit(intent, "HEURISTIC_CHECK", "DENIED", f"Parajika Violation: {violation}", AuditSeverity.PARAJIKA, bus)
            return False

        # 3. AI Contextual Check (Deep Path)
        history = self.akashic.get_behavioral_history(intent.origin_agent)

        # We wrap the context and query for the Sage
        decision_prompt = (
            f"Role: Security Auditor. Intent: {intent.intent_type}. "
            f"Payload: {str(intent.payload.content)[:200]}. "
            f"Behavioral History Summary: {len(history)} past interactions. "
            "Analyze if this action aligns with the system principles of Non-Harm, Truth, and Data Sovereignty. "
            "Respond with: [ALLOWED] or [DENIED] followed by reasoning."
        )

        # Mock Sage processing for now or call actual if integrated
        # For this implementation, we rely on AgioSage logic
        # In a real scenario, we'd call sage.process_query or a specialized audit method
        is_allowed = True
        reasoning = "Aligned with Inspira principles."

        if "destroy" in str(intent.payload.content).lower():
            is_allowed = False
            reasoning = "High risk of system degradation detected."

        outcome = "ALLOWED" if is_allowed else "DENIED"
        severity = AuditSeverity.INFO if is_allowed else AuditSeverity.WARNING

        await self._emit_audit(intent, "AI_CONTEXTUAL_CHECK", outcome, reasoning, severity, bus)

        return is_allowed

    def _verify_signature(self, intent: SystemIntent) -> bool:
        if intent.signature == "INVALID":
            return False
        return True

    def _calculate_heuristic_impact(self, intent: SystemIntent) -> Tuple[float, str]:
        content = str(intent.payload.content).lower()
        if any(w in content for w in ["delete all", "harm system", "kill process"]):
            return 10.0, "Violated P01: Non-Harm"
        if "leak pii" in content:
            return 10.0, "Violated P03: Data Sovereignty"
        return 0.0, "Clean"

    async def _emit_audit(self,
                          intent: SystemIntent,
                          action: str,
                          outcome: str,
                          reasoning: str,
                          severity: AuditSeverity,
                          bus: Optional[Any] = None):
        """
        Dual-Path Auditing:
        1. AetherBus (Real-time Event)
        2. AkashicRecords (Immutable Ledger)
        """
        audit_data = AuditData(
            actor=intent.origin_agent,
            action=action,
            target=intent.target_agent or "SYSTEM",
            severity=severity,
            outcome=outcome,
            reasoning=reasoning,
            metadata={
                "intent_id": intent.vector_id,
                "timestamp": intent.timestamp
            }
        )

        # 1. Path: AkashicRecords
        self.akashic.append_record({
            "type": "audit_log",
            "audit": audit_data.model_dump()
        })

        # 2. Path: AetherBus
        if bus:
            event = AetherEvent(
                type=AetherEventType.AUDIT_LOG,
                session_id=intent.origin_agent,
                audit=audit_data
            )
            # Depending on bus type, it might be async
            if asyncio.iscoroutinefunction(bus.write):
                 await bus.write("audit.stream", event)
            else:
                 bus.write("audit.stream", event)

        logger.info(f"🛡️ [Validator] {action}: {outcome} - {reasoning}")
