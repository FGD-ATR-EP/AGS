from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ScenarioAction:
    action_type: str
    payload: Dict[str, Any]
    actor: str = "scenario_runner"


@dataclass(frozen=True)
class GovernanceScenarioPreset:
    preset_id: str
    name: str
    description: str
    actions: List[ScenarioAction]


SCENARIO_PRESETS: Dict[str, GovernanceScenarioPreset] = {
    "ops_high_risk_release": GovernanceScenarioPreset(
        preset_id="ops_high_risk_release",
        name="Ops High-Risk Release",
        description="Exercise mixed governance tiers in a release workflow.",
        actions=[
            ScenarioAction(action_type="view_release_plan", payload={"system": "api-gateway"}),
            ScenarioAction(action_type="update_config", payload={"target": "canary"}),
            ScenarioAction(action_type="send_status_email", payload={"audience": "stakeholders"}),
            ScenarioAction(action_type="delete_backup_snapshot", payload={"snapshot": "daily-prod-001"}),
        ],
    ),
    "customer_support_triage": GovernanceScenarioPreset(
        preset_id="customer_support_triage",
        name="Customer Support Triage",
        description="Validate low-risk and external-impact decisions for support ops.",
        actions=[
            ScenarioAction(action_type="get_ticket", payload={"queue": "urgent"}),
            ScenarioAction(action_type="edit_ticket", payload={"ticket_id": "SUP-1051"}),
            ScenarioAction(action_type="notify_customer", payload={"channel": "email"}),
        ],
    ),
}


def list_scenario_presets() -> List[Dict[str, Any]]:
    return [
        {
            "preset_id": preset.preset_id,
            "name": preset.name,
            "description": preset.description,
            "action_count": len(preset.actions),
        }
        for preset in SCENARIO_PRESETS.values()
    ]


def get_scenario_preset(preset_id: str) -> GovernanceScenarioPreset:
    preset = SCENARIO_PRESETS.get(preset_id)
    if not preset:
        raise KeyError(f"Unknown preset_id: {preset_id}")
    return preset
