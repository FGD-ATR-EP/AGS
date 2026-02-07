from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MeterState(str, Enum):
    PREDICTABLE = "predictable"
    DIVERGENT = "divergent"
    CHAOTIC_GENIUS = "chaotic_genius"


class UserContext(BaseModel):
    current_screen: str
    previous_actions: List[str] = Field(default_factory=list)


class PredictionSnapshot(BaseModel):
    model_version: str
    predicted_action: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class MicroMetrics(BaseModel):
    typing_variance: float = Field(default=0.0, ge=0.0, le=1.0)
    hesitation_pauses: int = Field(default=0, ge=0)
    mouse_jitter: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    voice_tone_variance: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ActualAction(BaseModel):
    type: str
    content_hash: str
    input_method: str
    micro_metrics: MicroMetrics = Field(default_factory=MicroMetrics)
    content_preview: Optional[str] = Field(
        default=None,
        description="Optional short input preview used for semantic/noise validation.",
    )


class EntropyPacket(BaseModel):
    packet_id: UUID
    timestamp: datetime
    user_context: UserContext
    prediction_snapshot: PredictionSnapshot
    actual_action: ActualAction


class EntropyAssessment(BaseModel):
    packet_id: UUID
    qou_score: float = Field(ge=0.0, le=1.0)
    semantic_weight: float = Field(ge=0.0, le=1.0)
    safety_weight: float = Field(ge=0.0, le=1.0)
    surprise_factor: float = Field(ge=0.0, le=1.0)
    reward_amount: int = Field(ge=0)
    meter_state: MeterState
    preserve: bool = False
    trigger_model_update: bool = False
    anti_gaming_flag: Optional[str] = None


class EntropySubmitRequest(BaseModel):
    user_id: UUID
    packet: EntropyPacket


class EntropySubmitResponse(BaseModel):
    assessment: EntropyAssessment
    ledger_entry_id: UUID
    artifact_ref: Optional[str] = None
    hash_chain_head: str
