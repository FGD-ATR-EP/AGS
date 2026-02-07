import hashlib
from fastapi import APIRouter, HTTPException, Request

from src.backend.genesis_core.entropy.schemas import EntropySubmitRequest, EntropySubmitResponse

router = APIRouter(prefix="/api/v1/entropy", tags=["entropy-economy"])


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
