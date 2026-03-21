from enum import IntEnum
from typing import Any, Dict


class ActionTier(IntEnum):
    TIER_0_READ_ONLY = 0
    TIER_1_REVERSIBLE = 1
    TIER_2_EXTERNAL_IMPACT = 2
    TIER_3_SENSITIVE = 3


class RiskTiering:
    """Policy-independent action tier classifier (Tier 0-3)."""

    KEYWORDS = {
        ActionTier.TIER_0_READ_ONLY: {"read", "get", "list", "view", "inspect"},
        ActionTier.TIER_1_REVERSIBLE: {"create", "write", "update", "edit", "patch", "draft"},
        ActionTier.TIER_2_EXTERNAL_IMPACT: {"send", "post", "publish", "notify", "share", "deploy"},
        ActionTier.TIER_3_SENSITIVE: {"delete", "remove", "revoke", "payment", "withdraw", "drop", "chmod"},
    }

    @classmethod
    def classify(cls, action_type: str, payload: Dict[str, Any] | None = None) -> ActionTier:
        action = (action_type or "").lower()
        payload = payload or {}

        if payload.get("real_world") is True or payload.get("external_side_effect") is True:
            return ActionTier.TIER_2_EXTERNAL_IMPACT

        for tier in (ActionTier.TIER_3_SENSITIVE, ActionTier.TIER_2_EXTERNAL_IMPACT, ActionTier.TIER_1_REVERSIBLE):
            if any(k in action for k in cls.KEYWORDS[tier]):
                return tier

        return ActionTier.TIER_0_READ_ONLY
