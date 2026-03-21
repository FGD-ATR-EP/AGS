"""
Intent Vector: The Iron Core Data Structure
============================================
Implements the complete Intent Vector specification with:
- HMAC cryptographic signatures
- Canonical hashing for immutability
- Nanosecond precision timestamps
- Trust Score tracking
- Identity Annihilation (PII removal)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import hmac
import json
import time
import os

# Secret key for HMAC (in production, load from secure vault)
_HMAC_SECRET = os.getenv("AETHERIUM_HMAC_SECRET", "GENESIS_IRON_CORE_KEY").encode()

try:
    import xxhash
    _fast_hash = xxhash.xxh64
except ImportError:
    def _fast_hash(data):
        class MockHash:
            def __init__(self, d): self.d = d
            def hexdigest(self): return hashlib.sha256(self.d).hexdigest()
        return MockHash(data)


@dataclass(frozen=True)
class AetherEnvelope:
    """
    The Intent Vector - Iron Core Edition.
    
    Immutable data structure representing pure intent flowing through AetherBus.
    Implements Sopan Protocol Stage 2: AkashicEnvelope (Crystallization).
    
    Attributes:
        vector_id: One-way hash for audit trail (Akashic Record)
        timestamp_ns: Nanosecond precision timestamp for causal ordering
        type: Intent type (e.g., "USER.QUERY", "SYSTEM.TICK")
        payload: Pure intent data (PII-annihilated)
        context: Environmental sensors (light, sound, temperature, system vitals)
        from_agent: Source agent identifier
        to_target: Target agent or "BROADCAST"
        trust_score: Confidence level (0.0-1.0) for poison pill detection
        canonical_hash: Immutable content hash
        signature: HMAC signature for integrity verification
    """
    
    # Core Identity
    vector_id: str
    timestamp_ns: int  # Nanosecond precision
    type: str
    
    # Content
    payload: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Routing
    from_agent: str = "SYSTEM"
    to_target: str = "BROADCAST"
    
    # Security & Trust
    trust_score: float = 1.0
    canonical_hash: str = ""
    signature: str = ""
    
    def __post_init__(self):
        """
        Post-initialization to compute derived fields.
        Note: Since dataclass is frozen, we use object.__setattr__
        """
        # Compute canonical hash (deterministic content hash)
        canonical_content = self._get_canonical_content()
        canonical_hash = _fast_hash(canonical_content.encode()).hexdigest()
        object.__setattr__(self, 'canonical_hash', canonical_hash)
        
        # Compute HMAC signature
        signature = hmac.new(
            _HMAC_SECRET,
            canonical_content.encode(),
            hashlib.sha256
        ).hexdigest()
        object.__setattr__(self, 'signature', signature)
    
    def _get_canonical_content(self) -> str:
        """
        Generate canonical representation for hashing.
        Ensures deterministic ordering for cryptographic integrity.
        """
        return json.dumps({
            "vector_id": self.vector_id,
            "timestamp_ns": self.timestamp_ns,
            "type": self.type,
            "payload": self.payload,
            "context": self.context,
            "from_agent": self.from_agent,
            "to_target": self.to_target,
            "trust_score": self.trust_score
        }, sort_keys=True, separators=(',', ':'))
    
    def verify_signature(self, secret: bytes = _HMAC_SECRET) -> bool:
        """
        Verify HMAC signature integrity.
        
        Returns:
            True if signature is valid, False otherwise
        """
        canonical_content = self._get_canonical_content()
        expected_signature = hmac.new(
            secret,
            canonical_content.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(self.signature, expected_signature)
    
    def is_poison_pill(self, threshold: float = 0.5) -> bool:
        """
        Check if this intent is potentially malicious.
        
        Args:
            threshold: Minimum trust score required
            
        Returns:
            True if trust_score below threshold
        """
        return self.trust_score < threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "vector_id": self.vector_id,
            "timestamp_ns": self.timestamp_ns,
            "timestamp_iso": datetime.fromtimestamp(self.timestamp_ns / 1e9).isoformat(),
            "type": self.type,
            "from": self.from_agent,
            "to": self.to_target,
            "payload": self.payload,
            "context": self.context,
            "trust_score": self.trust_score,
            "canonical_hash": self.canonical_hash,
            "signature": self.signature
        }
    
    def __repr__(self):
        return f"<AetherEnvelope(id={self.vector_id[:8]}..., type={self.type}, from={self.from_agent}, trust={self.trust_score:.2f})>"


def create_intent(
    type: str,
    payload: Dict[str, Any],
    from_agent: str = "SYSTEM",
    to_target: str = "BROADCAST",
    context: Optional[Dict[str, Any]] = None,
    trust_score: float = 1.0
) -> AetherEnvelope:
    """
    Factory function to create Intent Vectors with automatic ID and timestamp.
    
    This is the recommended way to create AetherEnvelope instances.
    
    Args:
        type: Intent type (e.g., "USER.QUERY")
        payload: Intent data (should be PII-annihilated)
        from_agent: Source agent
        to_target: Target agent or "BROADCAST"
        context: Environmental context
        trust_score: Confidence level (0.0-1.0)
        
    Returns:
        Immutable AetherEnvelope instance
    """
    # Generate vector ID (one-way hash)
    vector_id = _fast_hash(
        f"{time.time_ns()}{from_agent}{type}".encode()
    ).hexdigest()
    
    # Nanosecond precision timestamp
    timestamp_ns = time.time_ns()
    
    return AetherEnvelope(
        vector_id=vector_id,
        timestamp_ns=timestamp_ns,
        type=type,
        payload=payload,
        context=context or {},
        from_agent=from_agent,
        to_target=to_target,
        trust_score=trust_score
    )


def annihilate_identity(data: Dict[str, Any], pii_fields: Optional[list] = None) -> Dict[str, Any]:
    """
    Identity Annihilation: Remove PII from payload.
    
    This implements the privacy-preserving transformation required
    before data enters the AetherBus.
    
    Args:
        data: Raw data potentially containing PII
        pii_fields: List of field names to remove (default: common PII fields)
        
    Returns:
        Sanitized data dictionary
    """
    if pii_fields is None:
        pii_fields = [
            "email", "phone", "ssn", "credit_card", "password",
            "address", "ip_address", "user_id", "session_id"
        ]
    
    sanitized = {}
    for key, value in data.items():
        if key.lower() in pii_fields:
            continue  # Skip PII fields
        
        if isinstance(value, dict):
            sanitized[key] = annihilate_identity(value, pii_fields)
        else:
            sanitized[key] = value
    
    return sanitized
