from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, Mapping, MutableMapping, Optional, Protocol

from src.backend.genesis_core.protocol.correlation import CorrelationPolicy
from src.backend.genesis_core.protocol.schemas import AetherEvent


BusCallback = Callable[[AetherEvent], Awaitable[None]]


class BusCodec(str, Enum):
    JSON = "json"
    MSGPACK = "msgpack"


class BusCompression(str, Enum):
    NONE = "none"
    ZLIB = "zlib"


class BusRole(str, Enum):
    INTERNAL = "internal"
    EXTERNAL = "external"


class BusAckStatus(str, Enum):
    ACCEPTED = "accepted"
    ERROR = "error"


@dataclass(frozen=True)
class BusEndpoint:
    role: BusRole
    transport: str
    address: str


@dataclass(frozen=True)
class BusReconnectPolicy:
    initial_delay_ms: int = 250
    max_delay_ms: int = 5_000
    max_attempts: int = 10


@dataclass(frozen=True)
class BusConfig:
    implementation: str = "tachyon"
    internal_endpoint: BusEndpoint = field(
        default_factory=lambda: BusEndpoint(
            role=BusRole.INTERNAL,
            transport="zeromq",
            address="tcp://127.0.0.1:5555",
        )
    )
    external_endpoint: BusEndpoint = field(
        default_factory=lambda: BusEndpoint(
            role=BusRole.EXTERNAL,
            transport="websocket",
            address="ws://127.0.0.1:5556/ws",
        )
    )
    codec: BusCodec = BusCodec.MSGPACK
    compression: BusCompression = BusCompression.NONE
    timeout_ms: int = 2_000
    reconnect: BusReconnectPolicy = field(default_factory=BusReconnectPolicy)
    enable_ack: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BusPublishRequest:
    event: AetherEvent
    topic: Optional[str] = None
    correlation_id: Optional[str] = None
    codec: Optional[BusCodec] = None
    compression: Optional[BusCompression] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BusAck:
    message_id: str
    status: BusAckStatus
    correlation_id: str
    detail: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SupportsBusWrite(Protocol):
    def write(self, topic: str, payload: Any) -> str: ...


class BusCodecAdapter(Protocol):
    def encode(self, payload: Mapping[str, Any]) -> bytes: ...
    def decode(self, payload: bytes) -> Dict[str, Any]: ...


class CorrelationMixin:
    @staticmethod
    def ensure_correlation_id(
        event: AetherEvent,
        metadata: Optional[MutableMapping[str, Any]] = None,
        correlation_id: Optional[str] = None,
        causation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> str:
        resolved = CorrelationPolicy.build(
            correlation_id=correlation_id or getattr(event, "correlation_id", None) or event.extensions.get("correlation_id"),
            causation_id=causation_id or getattr(event, "causation_id", None) or event.extensions.get("causation_id"),
            trace_id=trace_id or (correlation_id if correlation_id else None) or event.extensions.get("trace_id") or getattr(event, "trace_id", None),
            session_id=getattr(event, "session_id", None),
        )
        event.correlation_id = resolved["correlation_id"] or event.correlation_id
        event.causation_id = resolved["causation_id"]
        event.trace_id = resolved["trace_id"] or event.trace_id
        event.extensions["correlation_id"] = event.correlation_id
        event.extensions["causation_id"] = event.causation_id
        event.extensions["trace_id"] = event.trace_id
        if metadata is not None:
            metadata.update({k: v for k, v in resolved.items() if v is not None})
        return event.correlation_id
