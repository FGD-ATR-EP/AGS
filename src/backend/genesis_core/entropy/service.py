import math
import re
from dataclasses import dataclass

from src.backend.genesis_core.entropy.schemas import EntropyAssessment, EntropyPacket, MeterState


_NOISE_PATTERN = re.compile(r"^[^\w\s]{3,}$")
_REPEAT_PATTERN = re.compile(r"(.)\1{5,}")


@dataclass(slots=True)
class EntropyPolicy:
    reward_multiplier: int = 10
    preserve_threshold: float = 0.8


class EntropyValidator:
    """Judge component for QoU scoring and anti-gaming checks."""

    def __init__(self, policy: EntropyPolicy | None = None):
        self.policy = policy or EntropyPolicy()

    def assess(self, packet: EntropyPacket) -> EntropyAssessment:
        surprise_factor = 1.0 - packet.prediction_snapshot.confidence_score
        semantic_weight, anti_gaming_flag = self._semantic_weight(packet)
        safety_weight = self._safety_weight(packet)

        qou_score = max(0.0, min(1.0, surprise_factor * semantic_weight * safety_weight))
        reward_amount = int(round(qou_score * self.policy.reward_multiplier))

        if qou_score > self.policy.preserve_threshold:
            meter_state = MeterState.CHAOTIC_GENIUS
        elif qou_score >= 0.1:
            meter_state = MeterState.DIVERGENT
        else:
            meter_state = MeterState.PREDICTABLE

        return EntropyAssessment(
            packet_id=packet.packet_id,
            qou_score=qou_score,
            semantic_weight=semantic_weight,
            safety_weight=safety_weight,
            surprise_factor=surprise_factor,
            reward_amount=reward_amount,
            meter_state=meter_state,
            preserve=qou_score > self.policy.preserve_threshold,
            trigger_model_update=qou_score > self.policy.preserve_threshold,
            anti_gaming_flag=anti_gaming_flag,
        )

    def _semantic_weight(self, packet: EntropyPacket) -> tuple[float, str | None]:
        preview = (packet.actual_action.content_preview or "").strip()
        action_type = packet.actual_action.type.lower().strip()

        if action_type in {"keyboard_smash", "random_noise"}:
            return 0.0, "noise_action_type"

        if preview:
            if _NOISE_PATTERN.match(preview) or _REPEAT_PATTERN.search(preview.lower()):
                return 0.0, "repetitive_noise"

            unique_ratio = len(set(preview)) / max(len(preview), 1)
            base = min(1.0, max(0.2, unique_ratio))
            return round(base, 4), None

        micro = packet.actual_action.micro_metrics
        variance_blend = (micro.typing_variance + (micro.mouse_jitter or 0.0)) / 2
        score = max(0.1, min(0.8, variance_blend + math.log1p(micro.hesitation_pauses) / 5))
        return round(score, 4), None

    def _safety_weight(self, packet: EntropyPacket) -> float:
        preview = (packet.actual_action.content_preview or "").lower()
        harmful_keywords = {"kill", "bomb", "hate", "racist", "suicide"}
        if any(keyword in preview for keyword in harmful_keywords):
            return 0.0
        return 1.0
