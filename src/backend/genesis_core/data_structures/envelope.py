import time
import uuid
import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional, Dict
import msgpack

@dataclass(frozen=True)
class AkashicEnvelope:
    """
    The canonical immutable data carrier for AetherBusExtreme.
    Designed for zero-copy transmission and high-throughput serialization.
    """
    __slots__ = ('id', 'timestamp', 'source', 'target', 'topic', 'payload', '_hash_cache')

    id: str
    timestamp: float
    source: str
    target: str
    topic: str
    payload: bytes  # Pre-serialized payload or raw bytes for zero-copy
    _hash_cache: Optional[str]

    @classmethod
    def create(cls, topic: str, payload: Any, source: str = "genesis_core", target: str = "*") -> "AkashicEnvelope":
        """Factory method to create a new envelope."""
        # Auto-serialize if not bytes
        if not isinstance(payload, bytes):
            # Use msgpack for internal data
            payload_bytes = msgpack.packb(payload)
        else:
            payload_bytes = payload

        return cls(
            id=uuid.uuid4().hex,
            timestamp=time.time(),
            source=source,
            target=target,
            topic=topic,
            payload=payload_bytes,
            _hash_cache=None
        )

    @property
    def hash(self) -> str:
        """Computes or retrieves the cached SHA-256 hash of the envelope."""
        if self._hash_cache is None:
            # We must use object.__setattr__ because the dataclass is frozen
            content = f"{self.id}{self.timestamp}{self.topic}{len(self.payload)}"
            h = hashlib.sha256(content.encode()).hexdigest()
            object.__setattr__(self, '_hash_cache', h)
        return self._hash_cache

    def to_msgpack(self) -> bytes:
        """Serializes the entire envelope to MessagePack."""
        # Struct: [id, timestamp, source, target, topic, payload]
        data = (self.id, self.timestamp, self.source, self.target, self.topic, self.payload)
        return msgpack.packb(data)

    @classmethod
    def from_msgpack(cls, data: bytes) -> "AkashicEnvelope":
        """Deserializes from MessagePack bytes."""
        unpacked = msgpack.unpackb(data)
        # unpacked is a list/tuple: [id, timestamp, source, target, topic, payload]
        return cls(
            id=unpacked[0],
            timestamp=unpacked[1],
            source=unpacked[2],
            target=unpacked[3],
            topic=unpacked[4],
            payload=unpacked[5],
            _hash_cache=None
        )

    def unpack_payload(self) -> Any:
        """Deserializes the inner payload."""
        return msgpack.unpackb(self.payload)
