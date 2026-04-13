from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import logging

from src.backend.genesis_core.governance.core import ApprovalRequest
from src.backend.genesis_core.governance.scenario_presets import (
    get_scenario_preset,
    list_scenario_presets,
)
from src.backend.genesis_core.lifecycle import LifecycleManager
from src.backend.genesis_core.memory.akashic import MemoryProjectionManager

router = APIRouter(prefix="/governance", tags=["governance"])
logger = logging.getLogger("governance.router")

lifecycle = LifecycleManager()
memory_projection = MemoryProjectionManager(lifecycle.ledger)


@router.get("/approvals", response_model=List[ApprovalRequest])
async def get_pending_approvals():
    gov = lifecycle.validator.governance
    return list(gov.pending_approvals.values())


class ApprovalDecision(BaseModel):
    request_id: str
    decision: str  # APPROVED or REJECTED (case-insensitive)


@router.post("/decide")
async def handle_decision(decision: ApprovalDecision):
    gov = lifecycle.validator.governance
    success = gov.handle_approval(decision.request_id, decision.decision)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    normalized_decision = decision.decision.upper()
    return {"status": "success", "outcome": normalized_decision}


@router.get("/gems")
async def get_gems() -> Dict[str, Any]:
    gem_projection = memory_projection.get_gem_projection()
    gems = [entry["current"] for entry in gem_projection.get("gems", {}).values() if "current" in entry]
    return {"gems": gems}


class GemSimulationRequest(BaseModel):
    gem: Dict[str, Any]
    shadow_mode: bool = True


@router.post("/simulate-policy")
async def simulate_policy(request: GemSimulationRequest):
    gov = lifecycle.validator.governance
    return gov.simulate_rule_promotion(gem=request.gem, shadow_mode=request.shadow_mode)


@router.get("/scenario-presets")
async def get_scenario_presets() -> Dict[str, List[Dict[str, Any]]]:
    return {"presets": list_scenario_presets()}


class ScenarioPresetRunRequest(BaseModel):
    preset_id: str


@router.post("/scenario-presets/run")
async def run_scenario_preset(request: ScenarioPresetRunRequest) -> Dict[str, Any]:
    gov = lifecycle.validator.governance
    try:
        preset = get_scenario_preset(request.preset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info("Running governance scenario preset", extra={"preset_id": preset.preset_id})
    results: List[Dict[str, Any]] = []
    for scenario_action in preset.actions:
        tier = gov.assess_risk(action_type=scenario_action.action_type, payload=scenario_action.payload)
        status = "approval_required" if tier >= 2 else "auto_allow"
        results.append(
            {
                "action_type": scenario_action.action_type,
                "tier": int(tier),
                "status": status,
            }
        )

    return {
        "preset_id": preset.preset_id,
        "name": preset.name,
        "actions": results,
        "summary": {
            "total": len(results),
            "approval_required": len([r for r in results if r["status"] == "approval_required"]),
        },
    }
