from fastapi import APIRouter, HTTPException
from typing import List, Dict
from src.backend.genesis_core.governance.core import ApprovalRequest, ActionTier
from pydantic import BaseModel

router = APIRouter(prefix="/governance", tags=["governance"])

# This is a global instance for the demo/simulation
# In a real system, this would be injected or retrieved from a manager
from src.backend.genesis_core.lifecycle import LifecycleManager
lifecycle = LifecycleManager()

@router.get("/approvals", response_model=List[ApprovalRequest])
async def get_pending_approvals():
    gov = lifecycle.validator.governance
    return list(gov.pending_approvals.values())

class ApprovalDecision(BaseModel):
    request_id: str
    decision: str # APPROVED or REJECTED

@router.post("/decide")
async def handle_decision(decision: ApprovalDecision):
    gov = lifecycle.validator.governance
    success = gov.handle_approval(decision.request_id, decision.decision)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "success", "decision": decision.decision}

@router.get("/gems")
async def get_gems():
    # Placeholder for gem retrieval
    return []
