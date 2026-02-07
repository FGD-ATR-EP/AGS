import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.backend.genesis_core.entropy.schemas import EntropyAssessment


@dataclass(slots=True)
class EntropyLedgerEntry:
    id: UUID
    user_id: UUID
    qou_score: float
    reward_amount: int
    artifact_ref: Optional[str]
    created_at: datetime
    hash_prev: str
    hash_self: str


@dataclass(slots=True)
class AkashicTreasury:
    """Immutable-like ledger with hash-chain semantics for entropy records."""

    entries: list[EntropyLedgerEntry] = field(default_factory=list)

    @property
    def hash_head(self) -> str:
        if not self.entries:
            return "GENESIS"
        return self.entries[-1].hash_self

    def append(self, user_id: UUID, assessment: EntropyAssessment, artifact_ref: Optional[str]) -> EntropyLedgerEntry:
        entry_id = uuid4()
        created_at = datetime.utcnow()
        payload = {
            "id": str(entry_id),
            "user_id": str(user_id),
            "qou_score": assessment.qou_score,
            "reward_amount": assessment.reward_amount,
            "artifact_ref": artifact_ref,
            "created_at": created_at.isoformat(),
            "hash_prev": self.hash_head,
        }
        hash_self = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

        entry = EntropyLedgerEntry(
            id=entry_id,
            user_id=user_id,
            qou_score=assessment.qou_score,
            reward_amount=assessment.reward_amount,
            artifact_ref=artifact_ref,
            created_at=created_at,
            hash_prev=self.hash_head,
            hash_self=hash_self,
        )
        self.entries.append(entry)
        return entry
