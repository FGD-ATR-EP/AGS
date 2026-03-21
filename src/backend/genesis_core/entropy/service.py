import math
import re
from dataclasses import dataclass

from src.backend.genesis_core.entropy.schemas import EntropyAssessment, EntropyPacket, MeterState, QoUBand


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


class EntropyReplayStudio:
    """Creates replay artifacts to explain why QoU scored high or low."""

    def __init__(self, validator: EntropyValidator):
        self.validator = validator

    def replay(self, packet: EntropyPacket):
        from src.backend.genesis_core.entropy.schemas import (
            ReplayDocument,
            ReplayExplanation,
            ReplayTimelineEvent,
        )

        assessment = self.validator.assess(packet)
        quality_band = self._quality_band(assessment.qou_score)

        drivers = [
            f"Surprise factor {assessment.surprise_factor:.2f} from confidence {packet.prediction_snapshot.confidence_score:.2f}",
            f"Semantic weight {assessment.semantic_weight:.2f}",
            f"Safety weight {assessment.safety_weight:.2f}",
        ]
        if assessment.anti_gaming_flag:
            drivers.append(f"Anti-gaming triggered: {assessment.anti_gaming_flag}")

        risks = []
        if assessment.semantic_weight <= 0.2:
            risks.append("Input resembled low-information or noisy behavior")
        if assessment.safety_weight == 0.0:
            risks.append("Harmful keywords forced safety weight to zero")
        if assessment.surprise_factor < 0.2:
            risks.append("Low novelty due to high model confidence")

        explanation = ReplayExplanation(
            quality_band=quality_band,
            verdict=self._verdict(assessment),
            drivers=drivers,
            risks=risks,
        )

        documents = [
            ReplayDocument(
                document_id="packet-context",
                title="User Context Snapshot",
                summary=(
                    f"Screen {packet.user_context.current_screen}; "
                    f"previous actions: {', '.join(packet.user_context.previous_actions) or 'none'}"
                ),
            ),
            ReplayDocument(
                document_id="prediction-snapshot",
                title="Prediction Baseline",
                summary=(
                    f"Model {packet.prediction_snapshot.model_version} predicted "
                    f"'{packet.prediction_snapshot.predicted_action}' with "
                    f"confidence {packet.prediction_snapshot.confidence_score:.2f}"
                ),
            ),
            ReplayDocument(
                document_id="action-evidence",
                title="Observed Action",
                summary=(
                    f"Action type {packet.actual_action.type} via {packet.actual_action.input_method}; "
                    f"preview: {(packet.actual_action.content_preview or 'n/a')[:80]}"
                ),
            ),
            ReplayDocument(
                document_id="score-breakdown",
                title="QoU Breakdown",
                summary=(
                    f"QoU {assessment.qou_score:.2f} = surprise {assessment.surprise_factor:.2f} × "
                    f"semantic {assessment.semantic_weight:.2f} × safety {assessment.safety_weight:.2f}"
                ),
            ),
        ]

        timeline = [
            ReplayTimelineEvent(order=1, label="Predict", detail=documents[1].summary),
            ReplayTimelineEvent(order=2, label="Observe", detail=documents[2].summary),
            ReplayTimelineEvent(order=3, label="Validate", detail=(
                "Semantic and safety validators computed component weights"
            )),
            ReplayTimelineEvent(order=4, label="Assess QoU", detail=documents[3].summary),
            ReplayTimelineEvent(order=5, label="Classify", detail=(
                f"Meter state '{assessment.meter_state.value}' with reward {assessment.reward_amount}"
            )),
        ]

        return assessment, documents, timeline, explanation

    @staticmethod
    def _quality_band(score: float) -> QoUBand:
        if score >= 0.8:
            return QoUBand.HIGH
        if score >= 0.3:
            return QoUBand.MEDIUM
        return QoUBand.LOW

    @staticmethod
    def _verdict(assessment: EntropyAssessment) -> str:
        if assessment.qou_score >= 0.8:
            return "Session shows high exploratory value with usable semantic signal."
        if assessment.qou_score >= 0.3:
            return "Session has mixed novelty and utility; improvements are possible."
        return "Session scored low due to weak novelty, semantic signal, or safety penalties."
