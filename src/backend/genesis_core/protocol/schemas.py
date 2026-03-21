from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import uuid4

from src.backend.genesis_core.protocol.correlation import CorrelationPolicy

from pydantic import BaseModel, ConfigDict, Field, model_validator


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class AetherEventType(str, Enum):
    STATE_UPDATE = "state_update"
    INTENT_DETECTED = "intent_detected"
    CONFIDENCE_SHIFT = "confidence_shift"
    RESONANCE_PEAK = "resonance_peak"
    MANIFESTATION = "manifestation"
    DEGRADATION = "degradation"
    SILENCE = "silence"
    HANDSHAKE = "handshake"
    ERROR = "error"


class ResonanceForm(str, Enum):
    SPHERE = "sphere"
    CUBE = "cube"
    VORTEX = "vortex"
    GRID = "grid"
    NEBULA = "nebula"


class IntentVector(BaseModel):
    clarity: float = Field(..., ge=0.0, le=1.0)
    emotional_valence: float = Field(..., ge=-1.0, le=1.0)
    urgency: float = Field(..., ge=0.0, le=1.0)
    trust: float = Field(..., ge=0.0, le=1.0)


class IntentData(BaseModel):
    vector: IntentVector
    semantic_hint: Optional[str] = None
    raw_content: Optional[str] = None


class ManifestationData(BaseModel):
    intent: str
    resonance: float = Field(..., ge=0.0, le=1.0)
    form: ResonanceForm
    color: str
    content: Union[str, Dict[str, Any]]



class ManifestationDirectiveState(BaseModel):
    correlation_id: str
    trace_id: str
    causation_id: Optional[str] = None
    topic: str
    directive_type: str
    manifest_version: str = "2026.03-manifestation-v1"
    session_id: Optional[str] = None
    lifecycle_stage: Optional[str] = None
    sandbox: bool = False


class ManifestationDirectivePayload(BaseModel):
    directive_state: ManifestationDirectiveState
    render_state: Dict[str, Any] = Field(default_factory=dict)
    status: Dict[str, Any] = Field(default_factory=dict)
    replay: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: Dict[str, Any] = Field(default_factory=dict)
    semantic_source: str = "backend"

class StateData(BaseModel):
    state: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    energy: float = Field(..., ge=0.0, le=1.0)
    coherence: float = Field(..., ge=0.0, le=1.0)


class EnvelopeEndpoint(BaseModel):
    service: str
    subsystem: Optional[str] = None
    instance: Optional[str] = None
    channel: Optional[str] = None


class GovernanceMetadata(BaseModel):
    decision: Optional[str] = None
    risk_tier: Optional[str] = None
    policy_effect: Optional[str] = None
    approval_ticket_id: Optional[str] = None
    policy_mode: str = "enforce"
    validated: bool = False


class MemoryMetadata(BaseModel):
    ledger_event_type: Optional[str] = None
    ledger_record_id: Optional[str] = None
    causal_chain: list[str] = Field(default_factory=list)
    replayable: bool = True


class TimestampMetadata(BaseModel):
    created_at: str = Field(default_factory=_utc_now_iso)
    published_at: Optional[str] = None
    consumed_at: Optional[str] = None


class ContentMetadata(BaseModel):
    content_type: str = "application/json"
    content_encoding: str = "identity"
    content_compression: str = "none"
    codec: str = "json"


class AetherEvent(BaseModel):
    """
    Canonical V3 directive envelope for all cross-subsystem traffic.
    Legacy fields remain available only as compatibility shims.
    """

    model_config = ConfigDict(use_enum_values=True, extra="ignore", populate_by_name=True)

    envelope_version: str = "3.0.0"
    protocol_version: str = "2026.03"
    envelope_id: str = Field(default_factory=lambda: str(uuid4()))
    type: AetherEventType
    correlation_id: str = Field(default_factory=lambda: CorrelationPolicy.new_id("corr"))
    causation_id: Optional[str] = None
    trace_id: str = Field(default_factory=lambda: CorrelationPolicy.new_id("trace"))
    origin: EnvelopeEndpoint
    target: EnvelopeEndpoint
    topic: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    governance: GovernanceMetadata = Field(default_factory=GovernanceMetadata)
    memory: MemoryMetadata = Field(default_factory=MemoryMetadata)
    timestamps: TimestampMetadata = Field(default_factory=TimestampMetadata)
    content: ContentMetadata = Field(default_factory=ContentMetadata)
    session_id: Optional[str] = None
    state: Optional[StateData] = None
    manifestation: Optional[ManifestationData] = None
    intent: Optional[IntentData] = None
    error: Optional[str] = None
    extensions: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _upgrade_legacy_payload(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        upgraded = dict(data)
        upgraded.setdefault("envelope_version", "3.0.0")
        upgraded.setdefault("protocol_version", "2026.03")
        upgraded.setdefault("envelope_id", str(uuid4()))

        session_id = upgraded.get("session_id")
        legacy_topic = (upgraded.get("extensions") or {}).get("topic")
        upgraded.setdefault("topic", legacy_topic or session_id or upgraded.get("type") or "system.broadcast")
        upgraded.setdefault("correlation_id", (upgraded.get("extensions") or {}).get("correlation_id") or session_id or CorrelationPolicy.new_id("corr"))
        upgraded.setdefault("trace_id", (upgraded.get("extensions") or {}).get("trace_id") or upgraded.get("correlation_id"))

        if "origin" not in upgraded:
            upgraded["origin"] = {
                "service": (upgraded.get("extensions") or {}).get("origin_service", "genesis_core"),
                "subsystem": (upgraded.get("extensions") or {}).get("origin_subsystem", "body"),
                "channel": session_id,
            }
        if "target" not in upgraded:
            upgraded["target"] = {
                "service": (upgraded.get("extensions") or {}).get("target_service", "broadcast"),
                "subsystem": (upgraded.get("extensions") or {}).get("target_subsystem"),
                "channel": session_id or "*",
            }

        payload = dict(upgraded.get("payload") or {})
        for legacy_field in ("state", "manifestation", "intent", "error"):
            if upgraded.get(legacy_field) is not None and legacy_field not in payload:
                value = upgraded[legacy_field]
                payload[legacy_field] = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
        upgraded["payload"] = payload

        if "governance" not in upgraded:
            upgraded["governance"] = (upgraded.get("extensions") or {}).get("governance", {})
        if "memory" not in upgraded:
            upgraded["memory"] = (upgraded.get("extensions") or {}).get("memory", {})
        if "timestamps" not in upgraded:
            legacy_timestamp = upgraded.get("timestamp")
            upgraded["timestamps"] = {
                "created_at": datetime.fromtimestamp(legacy_timestamp, tz=timezone.utc).isoformat()
                if legacy_timestamp
                else _utc_now_iso()
            }
        if "content" not in upgraded:
            bus_metadata = (upgraded.get("extensions") or {}).get("bus_metadata", {})
            upgraded["content"] = {
                "content_type": "application/json",
                "content_encoding": bus_metadata.get("content_encoding", "identity"),
                "content_compression": bus_metadata.get("compression", "none"),
                "codec": bus_metadata.get("codec", "json"),
            }

        return upgraded

    @model_validator(mode="after")
    def _synchronize_compatibility_fields(self) -> "AetherEvent":
        if self.state is None and "state" in self.payload:
            self.state = StateData.model_validate(self.payload["state"])
        if self.manifestation is None and "manifestation" in self.payload:
            self.manifestation = ManifestationData.model_validate(self.payload["manifestation"])
        if self.intent is None and "intent" in self.payload:
            self.intent = IntentData.model_validate(self.payload["intent"])
        if self.error is None and self.payload.get("error") is not None:
            self.error = str(self.payload["error"])

        if "directive_state" in self.payload and isinstance(self.payload["directive_state"], dict):
            directive_state = dict(self.payload["directive_state"])
            directive_state.setdefault("correlation_id", self.correlation_id)
            directive_state.setdefault("causation_id", self.causation_id)
            directive_state.setdefault("trace_id", self.trace_id)
            directive_state.setdefault("topic", self.topic)
            directive_state.setdefault("directive_type", self.type)
            directive_state.setdefault("session_id", self.session_id)
            directive_state.setdefault("manifest_version", "2026.03-manifestation-v1")
            self.payload["directive_state"] = directive_state

        correlation_metadata = CorrelationPolicy.build(
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            trace_id=self.trace_id,
            session_id=self.session_id,
        )
        self.correlation_id = correlation_metadata["correlation_id"] or self.correlation_id
        self.causation_id = correlation_metadata["causation_id"]
        self.trace_id = correlation_metadata["trace_id"] or self.trace_id
        self.extensions.setdefault("correlation_id", self.correlation_id)
        self.extensions.setdefault("causation_id", self.causation_id)
        self.extensions.setdefault("trace_id", self.trace_id)
        self.extensions.setdefault("topic", self.topic)
        self.extensions.setdefault("governance", self.governance.model_dump(mode="json"))
        self.extensions.setdefault("memory", self.memory.model_dump(mode="json"))
        self.extensions.setdefault("bus_metadata", {})
        self.extensions["bus_metadata"].setdefault("codec", self.content.codec)
        self.extensions["bus_metadata"].setdefault("compression", self.content.content_compression)
        self.extensions["bus_metadata"].setdefault("content_encoding", self.content.content_encoding)
        return self

