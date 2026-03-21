import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional
from uuid import UUID, uuid4

from src.backend.genesis_core.entropy.schemas import EntropyAssessment, QoUBand


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
        created_at = datetime.now(UTC)
        hash_prev = self.hash_head
        hash_self = self._compute_hash(
            entry_id=entry_id,
            user_id=user_id,
            qou_score=assessment.qou_score,
            reward_amount=assessment.reward_amount,
            artifact_ref=artifact_ref,
            created_at=created_at,
            hash_prev=hash_prev,
        )

        entry = EntropyLedgerEntry(
            id=entry_id,
            user_id=user_id,
            qou_score=assessment.qou_score,
            reward_amount=assessment.reward_amount,
            artifact_ref=artifact_ref,
            created_at=created_at,
            hash_prev=hash_prev,
            hash_self=hash_self,
        )
        self.entries.append(entry)
        return entry

    def qou_band_for_score(self, qou_score: float) -> QoUBand:
        if qou_score < 0.33:
            return QoUBand.LOW
        if qou_score < 0.66:
            return QoUBand.MEDIUM
        return QoUBand.HIGH

    def verify_continuity(self, entries: Optional[list[EntropyLedgerEntry]] = None) -> tuple[bool, list[dict[str, str]]]:
        target_entries = entries if entries is not None else self.entries
        issues: list[dict[str, str]] = []
        expected_prev = "GENESIS"

        for entry in target_entries:
            if entry.hash_prev != expected_prev:
                issues.append({"entry_id": str(entry.id), "issue": "hash_prev_mismatch"})

            recomputed = self._compute_hash(
                entry_id=entry.id,
                user_id=entry.user_id,
                qou_score=entry.qou_score,
                reward_amount=entry.reward_amount,
                artifact_ref=entry.artifact_ref,
                created_at=entry.created_at,
                hash_prev=entry.hash_prev,
            )
            if recomputed != entry.hash_self:
                issues.append({"entry_id": str(entry.id), "issue": "hash_self_integrity_failure"})

            expected_prev = entry.hash_self

        return len(issues) == 0, issues

    def _compute_hash(
        self,
        *,
        entry_id: UUID,
        user_id: UUID,
        qou_score: float,
        reward_amount: int,
        artifact_ref: Optional[str],
        created_at: datetime,
        hash_prev: str,
    ) -> str:
        payload = {
            "id": str(entry_id),
            "user_id": str(user_id),
            "qou_score": qou_score,
            "reward_amount": reward_amount,
            "artifact_ref": artifact_ref,
            "created_at": created_at.isoformat(),
            "hash_prev": hash_prev,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
