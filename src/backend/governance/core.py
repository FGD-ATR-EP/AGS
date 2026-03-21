import time
import uuid

from src.backend.genesis_core.protocol.correlation import CorrelationPolicy
from src.backend.genesis_core.protocol.schemas import AetherEvent
from dataclasses import asdict, dataclass
from typing import Any, Dict

from src.backend.governance.approval_router import ApprovalRouter, ApprovalTicket
from src.backend.governance.policy_engine import PolicyEngine, PolicyResult, default_policy_engine
from src.backend.governance.risk_tiering import ActionTier, RiskTiering


@dataclass
class GovernanceEnvelopeContext:
    envelope_id: str
    correlation: Dict[str, Any]
    session_id: str | None
    origin: Dict[str, Any]
    target: Dict[str, Any]
    topic: str
    action: str
    resource: str
    payload: Dict[str, Any]
    environment: str
    governance: Dict[str, Any]
    memory: Dict[str, Any]


@dataclass
class GovernanceDecision:
    status: str
    risk_tier: ActionTier
    reason: str
    action: str
    resource: str
    policy_effect: str | None = None
    policy_mode: str = "enforce"
    ticket_id: str | None = None
    recommendation: str | None = None
    ledger_event_type: str | None = None


class GovernanceCore:
    """First-class governance runtime: tiering + policy + approval + containment."""

    def __init__(self, ledger=None, policy_engine: PolicyEngine | None = None, approval_router: ApprovalRouter | None = None):
        self.ledger = ledger
        self.policy_engine = policy_engine or default_policy_engine()
        self.approval_router = approval_router or ApprovalRouter()

    def validate_envelope(self, envelope: AetherEvent) -> AetherEvent:
        validated = AetherEvent.model_validate(envelope.model_dump(mode="json"))
        validated.governance.validated = True
        if not validated.correlation_id:
            raise ValueError("Governance gate requires correlation_id")
        return validated

    def build_context(self, envelope: AetherEvent) -> GovernanceEnvelopeContext:
        envelope = self.validate_envelope(envelope)
        payload = envelope.payload or {}
        action = str(
            payload.get("action")
            or payload.get("intent_type")
            or payload.get("directive_type")
            or envelope.type
        ).lower()
        resource = str(
            payload.get("resource")
            or payload.get("topic")
            or envelope.topic
            or envelope.target.channel
            or envelope.target.service
        )
        return GovernanceEnvelopeContext(
            envelope_id=envelope.envelope_id,
            correlation=CorrelationPolicy.build(
                correlation_id=envelope.correlation_id,
                causation_id=envelope.causation_id,
                trace_id=envelope.trace_id,
                session_id=envelope.session_id,
            ),
            session_id=envelope.session_id,
            origin=envelope.origin.model_dump(mode="json"),
            target=envelope.target.model_dump(mode="json"),
            topic=envelope.topic,
            action=action,
            resource=resource,
            payload=payload,
            environment=str(payload.get("environment") or envelope.extensions.get("environment") or "development"),
            governance=envelope.governance.model_dump(mode="json"),
            memory=envelope.memory.model_dump(mode="json"),
        )

    def evaluate_envelope(self, envelope: AetherEvent, dry_run: bool = False) -> GovernanceDecision:
        context = self.build_context(envelope)
        return self.evaluate_action(
            action=context.action,
            resource=context.resource,
            payload=context.payload,
            dry_run=dry_run,
            correlation_metadata=context.correlation,
            envelope_context=context,
        )

    def evaluate_action(
        self,
        action: str,
        resource: str,
        payload: Dict[str, Any] | None = None,
        dry_run: bool = False,
        correlation_metadata: Dict[str, Any] | None = None,
        envelope_context: GovernanceEnvelopeContext | None = None,
    ) -> GovernanceDecision:
        payload = payload or {}
        correlation = CorrelationPolicy.build(
            correlation_id=(correlation_metadata or {}).get("correlation_id") or payload.get("correlation_id"),
            causation_id=(correlation_metadata or {}).get("causation_id") or payload.get("causation_id"),
            trace_id=(correlation_metadata or {}).get("trace_id") or payload.get("trace_id"),
            fallback=action,
        )
        tier = RiskTiering.classify(action, payload)

        context = {
            "action": action,
            "resource": resource,
            "payload": payload,
            "environment": payload.get("environment", "development"),
            "risk_tier": tier,
            "envelope": asdict(envelope_context) if envelope_context else None,
        }
        policy: PolicyResult = self.policy_engine.evaluate(context, dry_run=dry_run)
        mode_suffix = "_dry_run" if dry_run else ""
        reason = f"[DRY-RUN] {policy.reason}" if dry_run else policy.reason
        mode = "dry_run" if dry_run else policy.mode

        if policy.effect == "DENY":
            decision = GovernanceDecision(
                status="DENIED",
                risk_tier=tier,
                reason=reason,
                action=action,
                resource=resource,
                policy_effect=policy.effect,
                policy_mode=mode,
                recommendation="suspend",
                ledger_event_type=f"governance_denied{mode_suffix}",
            )
            self._record(f"governance_denied{mode_suffix}", decision, policy, correlation, envelope_context)
            return decision

        if policy.effect == "REQUIRE_APPROVAL":
            if dry_run:
                decision = GovernanceDecision(
                    status="PENDING_APPROVAL",
                    risk_tier=tier,
                    reason=reason,
                    action=action,
                    resource=resource,
                    policy_effect=policy.effect,
                    policy_mode=mode,
                    ticket_id="DRY-RUN",
                    ledger_event_type=f"governance_pending_approval{mode_suffix}",
                )
                self._record(f"governance_pending_approval{mode_suffix}", decision, policy, correlation, envelope_context)
                return decision

            ticket = ApprovalTicket(
                ticket_id=str(uuid.uuid4()),
                action=action,
                resource=resource,
                risk_tier=tier,
                impact=payload.get("impact", "External side effect may occur"),
                evidence=payload.get("evidence", {}),
            )
            self.approval_router.enqueue(ticket)
            decision = GovernanceDecision(
                status="PENDING_APPROVAL",
                risk_tier=tier,
                reason=reason,
                action=action,
                resource=resource,
                policy_effect=policy.effect,
                policy_mode=mode,
                ticket_id=ticket.ticket_id,
                ledger_event_type="governance_pending_approval",
            )
            self._record("governance_pending_approval", decision, policy, correlation, envelope_context)
            return decision

        decision = GovernanceDecision(
            status="ALLOWED",
            risk_tier=tier,
            reason=reason,
            action=action,
            resource=resource,
            policy_effect=policy.effect,
            policy_mode=mode,
            ledger_event_type=f"governance_allowed{mode_suffix}",
        )
        self._record(f"governance_allowed{mode_suffix}", decision, policy, correlation, envelope_context)
        return decision

    def recommend_recovery(self, event: Dict[str, Any]) -> Dict[str, str]:
        severity = str(event.get("severity", "low")).lower()
        if severity in {"critical", "high"}:
            recommendation = {"mode": "rollback", "reason": "High severity incident"}
        elif event.get("uncertain_state", False):
            recommendation = {"mode": "quarantine", "reason": "State uncertainty detected"}
        else:
            recommendation = {"mode": "suspend", "reason": "Safety-first manual inspection"}

        if self.ledger:
            self.ledger.append_record(payload={"type": "governance_recovery_recommendation", **recommendation}, actor="governance", correlation=CorrelationPolicy.build(fallback="governance_recovery_recommendation"))
        return recommendation

    def _record(
        self,
        event_type: str,
        decision: GovernanceDecision,
        policy: PolicyResult,
        correlation: Dict[str, Any],
        envelope_context: GovernanceEnvelopeContext | None,
    ) -> None:
        if not self.ledger:
            return
        self.ledger.append_record(
            payload={
                "type": event_type,
                "action": decision.action,
                "resource": decision.resource,
                "decision": asdict(decision),
                "policy": {
                    "effect": policy.effect,
                    "metadata": policy.metadata,
                    "mode": policy.mode,
                },
                "envelope": asdict(envelope_context) if envelope_context else None,
                "timestamp": time.time(),
                "correlation": correlation,
            },
            actor="governance",
            intent_id=decision.ticket_id,
            correlation=correlation,
        )
