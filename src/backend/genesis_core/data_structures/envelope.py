from __future__ import annotations

import warnings
from typing import Any, Dict

import msgpack

from src.backend.genesis_core.protocol.schemas import AetherEvent


class AkashicEnvelope:
    """
    Compatibility wrapper around the canonical V3 AetherEvent envelope.
    New code should use AetherEvent directly.
    """

    def __init__(self, event: AetherEvent):
        self.event = AetherEvent.model_validate(event)

    @classmethod
    def create(cls, topic: str, payload: Any, source: str = "genesis_core", target: str = "*") -> "AkashicEnvelope":
        warnings.warn(
            "AkashicEnvelope.create() is deprecated; use AetherEvent directly.",
            DeprecationWarning,
            stacklevel=2,
        )
        event = AetherEvent(
            type="state_update",
            topic=topic,
            origin={"service": source, "subsystem": "memory"},
            target={"service": target, "subsystem": "bus"},
            payload=payload if isinstance(payload, dict) else {"data": payload},
        )
        return cls(event)

    @property
    def id(self) -> str:
        return self.event.envelope_id

    @property
    def timestamp(self) -> str:
        return self.event.timestamps.created_at

    @property
    def source(self) -> str:
        return self.event.origin.service

    @property
    def target(self) -> str:
        return self.event.target.service

    @property
    def topic(self) -> str:
        return self.event.topic

    @property
    def payload(self) -> bytes:
        return msgpack.packb(self.event.payload, use_bin_type=True)

    def to_msgpack(self) -> bytes:
        return msgpack.packb(self.event.model_dump(mode="json"), use_bin_type=True)

    @classmethod
    def from_msgpack(cls, data: bytes) -> "AkashicEnvelope":
        unpacked: Dict[str, Any] = msgpack.unpackb(data, raw=False)
        return cls(AetherEvent.model_validate(unpacked))

    def unpack_payload(self) -> Any:
        return self.event.payload

