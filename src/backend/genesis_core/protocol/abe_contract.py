from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
import datetime

class AetherIdentity(BaseModel):
    """
    The permanent identity of the connecting entity.
    """
    issuer: str = Field(default="AETHERIUM", description="Authority issuing the identity")
    abe_id: str = Field(..., description="Unique ID for this contract (UUID)")
    entity_name: str = Field(..., description="Human readable name of the system/user")
    created_at: float = Field(default_factory=lambda: datetime.datetime.now().timestamp())

class AetherIntentDeclaration(BaseModel):
    """
    Declaration of what the entity intends to do.
    """
    primary_intent: str = Field(..., description="OBSERVER, CONTRIBUTOR, HYBRID")
    data_sensitivity: str = Field(default="LOW", description="LOW, HIGH, CRITICAL")
    expected_throughput: str = Field(default="LOW", description="LOW, MEDIUM, HIGH")

class ABEContract(BaseModel):
    """
    The .abe Connection Contract.
    Identity + Intent + Signature.
    This file defines WHO is connecting and WHY.
    """
    abe_version: str = Field(default="1.0")
    identity: AetherIdentity
    intent: AetherIntentDeclaration
    capabilities: List[str] = Field(default_factory=list, description="Requested capabilities e.g. ['subscribe', 'publish']")
    extensions: Dict[str, Any] = Field(default_factory=dict)

    # Signatures
    contract_signature: Optional[str] = Field(None, description="Cryptographic signature of the contract content")

    @field_validator('abe_id', check_fields=False)
    def validate_uuid(cls, v, values):
        # Validation logic if needed
        return v

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "ABEContract":
        return cls.model_validate_json(json_str)

    @classmethod
    def create_new(cls, entity_name: str, intent_type: str) -> "ABEContract":
        """Factory method to generate a new contract."""
        return cls(
            identity=AetherIdentity(
                abe_id=f"abe-{uuid.uuid4().hex[:12]}",
                entity_name=entity_name
            ),
            intent=AetherIntentDeclaration(
                primary_intent=intent_type
            ),
            capabilities=["subscribe"] # Default capability
        )
