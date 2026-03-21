from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Mapping

from pydantic import BaseModel, Field

from src.backend.genesis_core.memory.akashic import AkashicRecords
from src.backend.genesis_core.protocol.schemas import AetherEvent


ALLOWED_SECRET_REFERENCE_PREFIXES = ("env:", "secret://", "vault://", "aws-sm://", "gcp-sm://", "azure-kv://")
FORBIDDEN_SECRET_KEYS = {
    "api_key",
    "apikey",
    "token",
    "secret",
    "secret_key",
    "client_secret",
    "password",
    "credential",
    "credentials",
    "access_key",
}


@dataclass
class ActionPreview:
    plan: str
    diff: str
    tools: list[str]
    evidence: Dict[str, Any]


class DirectivePayload(BaseModel):
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    execution_scope: Dict[str, Any]
    actor: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionVessel(ABC):
    def __init__(self, name: str, ledger: AkashicRecords | None = None):
        self.name = name
        self.ledger = ledger or AkashicRecords()

    def preview(self, directive: AetherEvent | Dict[str, Any]) -> ActionPreview:
        envelope = self._coerce_envelope(directive)
        payload = self._extract_payload(envelope)
        return self._preview(envelope, payload)

    def execute(self, directive: AetherEvent | Dict[str, Any]) -> Dict[str, Any]:
        envelope = self._coerce_envelope(directive)
        payload = self._validate_execution_preconditions(envelope)
        result = self._execute(envelope, payload)
        return self._record_outcome(envelope, payload, result)

    @abstractmethod
    def _preview(self, envelope: AetherEvent, payload: DirectivePayload) -> ActionPreview:
        raise NotImplementedError

    @abstractmethod
    def _execute(self, envelope: AetherEvent, payload: DirectivePayload) -> Dict[str, Any]:
        raise NotImplementedError

    def _coerce_envelope(self, directive: AetherEvent | Dict[str, Any]) -> AetherEvent:
        return directive if isinstance(directive, AetherEvent) else AetherEvent.model_validate(directive)

    def _extract_payload(self, envelope: AetherEvent) -> DirectivePayload:
        payload = DirectivePayload.model_validate(envelope.payload)
        self._validate_correlation(envelope)
        self._validate_actor_identity(envelope, payload)
        self._validate_execution_scope(payload)
        self._validate_secret_references(payload.params)
        return payload

    def _validate_execution_preconditions(self, envelope: AetherEvent) -> DirectivePayload:
        payload = self._extract_payload(envelope)
        governance = envelope.governance
        if not governance.validated:
            raise PermissionError("Directive execution requires validated governance metadata")
        if governance.decision not in {"ALLOWED", "ALLOW"}:
            raise PermissionError("Directive execution requires an allowed governance decision")
        return payload

    def _validate_correlation(self, envelope: AetherEvent) -> None:
        if not envelope.correlation_id or not envelope.trace_id:
            raise ValueError("Directive envelope must include correlation_id and trace_id")

    def _validate_actor_identity(self, envelope: AetherEvent, payload: DirectivePayload) -> None:
        actor_identity = payload.actor or {}
        source_service = envelope.origin.service if envelope.origin else None
        if not actor_identity.get("id"):
            raise ValueError("Directive payload must include actor.id")
        if not actor_identity.get("type"):
            raise ValueError("Directive payload must include actor.type")
        if not source_service:
            raise ValueError("Directive envelope must include origin.service")

    def _validate_execution_scope(self, payload: DirectivePayload) -> None:
        scope = payload.execution_scope or {}
        if not scope.get("system"):
            raise ValueError("Directive payload must declare execution_scope.system")
        if not scope.get("permissions"):
            raise ValueError("Directive payload must declare execution_scope.permissions")

    def _validate_secret_references(self, data: Mapping[str, Any]) -> None:
        for key, value in data.items():
            normalized_key = str(key).lower()
            if isinstance(value, Mapping):
                self._validate_secret_references(value)
                continue
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Mapping):
                        self._validate_secret_references(item)
                continue
            if normalized_key not in FORBIDDEN_SECRET_KEYS:
                continue
            if value in (None, ""):
                continue
            if isinstance(value, str) and (
                value.startswith(ALLOWED_SECRET_REFERENCE_PREFIXES)
                or (value.startswith("${") and value.endswith("}"))
            ):
                continue
            raise ValueError(
                f"Directive params for '{key}' must use .env/secret-manager references, not hardcoded credentials"
            )

    def _record_outcome(
        self,
        envelope: AetherEvent,
        payload: DirectivePayload,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        outcome_payload = {
            "type": "execution_outcome",
            "vessel": self.name,
            "action": payload.action,
            "result": result,
            "correlation_id": envelope.correlation_id,
            "causation_id": envelope.envelope_id,
            "trace_id": envelope.trace_id,
            "execution_scope": payload.execution_scope,
            "governance": envelope.governance.model_dump(mode="json"),
            "actor": payload.actor,
            "source": envelope.origin.model_dump(mode="json"),
        }
        ledger_hash = self.ledger.append_record(
            payload=outcome_payload,
            actor=f"vessel:{self.name}",
            intent_id=envelope.envelope_id,
            causal_link=envelope.causation_id or envelope.envelope_id,
            correlation={
                "correlation_id": envelope.correlation_id,
                "causation_id": envelope.envelope_id,
                "trace_id": envelope.trace_id,
            },
        )
        response = dict(result)
        response.setdefault("memory", {})
        response["memory"]["ledger_record_id"] = ledger_hash
        response["memory"]["correlation_id"] = envelope.correlation_id
        return response
