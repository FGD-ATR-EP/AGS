from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Any, Dict

from src.backend.genesis_core.models.logenesis import IntentVector


class FaultType(str, Enum):
    SIGNAL_NOISE = "signal_noise"
    CONTEXT_DROPOUT = "context_dropout"
    URGENCY_SPIKE = "urgency_spike"
    PRECISION_DECAY = "precision_decay"


@dataclass
class FaultInjectionEvent:
    fault_type: FaultType
    severity: float
    canonical_keys: Dict[str, Any]


class FaultInjector:
    """Injects controlled anomalies to train Resonators in uncertain conditions."""

    def __init__(self, enabled: bool = False, intensity: float = 0.25, seed: int = 2026):
        self.enabled = enabled
        self.intensity = max(0.0, min(1.0, intensity))
        self._rng = Random(seed)

    def inject(self, vector: IntentVector) -> tuple[IntentVector, FaultInjectionEvent | None]:
        if not self.enabled:
            return vector, None

        fault_type = self._rng.choice(list(FaultType))
        severity = round(self._rng.uniform(0.1, self.intensity or 0.1), 3)
        updated = vector.model_copy(deep=True)

        if fault_type == FaultType.SIGNAL_NOISE:
            updated.subjective_weight = self._clamp(updated.subjective_weight + severity)
            updated.epistemic_need = self._clamp(updated.epistemic_need - severity * 0.5)
        elif fault_type == FaultType.CONTEXT_DROPOUT:
            updated.epistemic_need = self._clamp(updated.epistemic_need * (1 - severity))
            updated.precision_required = self._clamp(updated.precision_required * (1 - severity * 0.6))
        elif fault_type == FaultType.URGENCY_SPIKE:
            updated.decision_urgency = self._clamp(updated.decision_urgency + severity)
        elif fault_type == FaultType.PRECISION_DECAY:
            updated.precision_required = self._clamp(updated.precision_required - severity)

        event = FaultInjectionEvent(
            fault_type=fault_type,
            severity=severity,
            canonical_keys={
                "fault_type": fault_type.value,
                "severity": severity,
                "quality_confidence": round(1.0 - severity, 3),
                "quality_freshness": 1.0,
                "quality_completeness": round(max(0.0, 1.0 - severity * 0.5), 3),
            },
        )
        return updated, event

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
