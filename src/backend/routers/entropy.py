import logging
import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request

from src.backend.genesis_core.entropy.schemas import (
    EntropyLedgerExploreResponse,
    EntropyLedgerEntryView,
    EntropyReplayResponse,
    EntropySubmitRequest,
    EntropySubmitResponse,
    HashChainContinuityReport,
    HashChainIssue,
    QoUBand,
)

router = APIRouter(prefix="/api/v1/entropy", tags=["entropy-economy"])


logger = logging.getLogger("entropy.router")


@router.post("/submit", response_model=EntropySubmitResponse)
async def submit_entropy_packet(payload: EntropySubmitRequest, request: Request):
    app_state = request.app.state
    validator = getattr(app_state, "entropy_validator", None)
    treasury = getattr(app_state, "akashic_treasury", None)

    if validator is None or treasury is None:
        raise HTTPException(status_code=503, detail="Entropy subsystem is not initialized")

    assessment = validator.assess(payload.packet)

    artifact_ref = None
    if assessment.preserve:
        artifact_ref = f"akashic://entropy/{payload.packet.packet_id}"

    ledger_entry = treasury.append(
        user_id=payload.user_id,
        assessment=assessment,
        artifact_ref=artifact_ref,
    )

    if assessment.preserve:
        digest = hashlib.sha256(payload.packet.model_dump_json().encode()).hexdigest()
        artifact_ref = f"{artifact_ref}#{digest[:16]}"

    return EntropySubmitResponse(
        assessment=assessment,
        ledger_entry_id=ledger_entry.id,
        artifact_ref=artifact_ref,
        hash_chain_head=treasury.hash_head,
    )


@router.get("/ledger/explorer", response_model=EntropyLedgerExploreResponse)
async def explore_entropy_ledger(
    request: Request,
    start_time: Optional[datetime] = Query(default=None),
    end_time: Optional[datetime] = Query(default=None),
    qou_bands: list[QoUBand] = Query(default=[]),
    user_id: Optional[UUID] = Query(default=None),
):
    treasury = getattr(request.app.state, "akashic_treasury", None)
    if treasury is None:
        raise HTTPException(status_code=503, detail="Entropy subsystem is not initialized")

    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=400, detail="start_time must be <= end_time")

    filtered_entries = treasury.entries

    if start_time:
        filtered_entries = [entry for entry in filtered_entries if entry.created_at >= start_time]
    if end_time:
        filtered_entries = [entry for entry in filtered_entries if entry.created_at <= end_time]
    if user_id:
        filtered_entries = [entry for entry in filtered_entries if entry.user_id == user_id]

    if qou_bands:
        accepted = set(qou_bands)
        filtered_entries = [
            entry for entry in filtered_entries if treasury.qou_band_for_score(entry.qou_score) in accepted
        ]

    contiguous, issues = treasury.verify_continuity(filtered_entries)
    entry_views = [
        EntropyLedgerEntryView(
            id=entry.id,
            user_id=entry.user_id,
            qou_score=entry.qou_score,
            qou_band=treasury.qou_band_for_score(entry.qou_score),
            reward_amount=entry.reward_amount,
            artifact_ref=entry.artifact_ref,
            created_at=entry.created_at,
            hash_prev=entry.hash_prev,
            hash_self=entry.hash_self,
        )
        for entry in filtered_entries
    ]

    return EntropyLedgerExploreResponse(
        start_time=start_time,
        end_time=end_time,
        qou_bands=qou_bands,
        user_id=user_id,
        total_entries=len(entry_views),
        hash_chain_head=treasury.hash_head,
        continuity=HashChainContinuityReport(
            checked_entries=len(entry_views),
            contiguous=contiguous,
            issues=[HashChainIssue(entry_id=issue["entry_id"], issue=issue["issue"]) for issue in issues],
        ),
        entries=entry_views,
    )


@router.post("/replay", response_model=EntropyReplayResponse)
async def replay_entropy_packet(payload: EntropySubmitRequest, request: Request):
    replay_studio = getattr(request.app.state, "entropy_replay_studio", None)
    if replay_studio is None:
        raise HTTPException(status_code=503, detail="Entropy replay subsystem is not initialized")

    logger.info("entropy_replay_requested", extra={"packet_id": str(payload.packet.packet_id), "user_id": str(payload.user_id)})
    assessment, documents, timeline, explanation = replay_studio.replay(payload.packet)

    return EntropyReplayResponse(
        assessment=assessment,
        documents=documents,
        timeline=timeline,
        explanation=explanation,
    )
