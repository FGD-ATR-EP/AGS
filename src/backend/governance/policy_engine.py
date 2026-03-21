from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from src.backend.governance.risk_tiering import ActionTier


@dataclass
class PolicyResult:
    effect: str
    reason: str
    metadata: Dict[str, Any]
    mode: str = "enforce"


class PolicyEngine:
    """Minimal policy-as-code engine with composable python rules."""

    def __init__(self) -> None:
        self._rules: List[Callable[[Dict[str, Any]], PolicyResult | None]] = []

    def register(self, rule: Callable[[Dict[str, Any]], PolicyResult | None]) -> None:
        self._rules.append(rule)

    def evaluate(self, context: Dict[str, Any], dry_run: bool = False) -> PolicyResult:
        for rule in self._rules:
            verdict = rule(context)
            if verdict is not None:
                verdict.mode = "dry_run" if dry_run else "enforce"
                return verdict
        return PolicyResult(
            effect="ALLOW",
            reason="No matching policy rule",
            metadata={"dry_run": dry_run},
            mode="dry_run" if dry_run else "enforce",
        )


def default_policy_engine() -> PolicyEngine:
    engine = PolicyEngine()

    def deny_prod_secret_write(ctx: Dict[str, Any]) -> PolicyResult | None:
        resource = str(ctx.get("resource", ""))
        if "secret" in resource and ctx.get("environment") == "production":
            return PolicyResult(
                effect="DENY",
                reason="Secret mutation is denied in production",
                metadata={"control": "secrets_hardening"},
            )
        return None

    def require_human_for_high_risk(ctx: Dict[str, Any]) -> PolicyResult | None:
        tier = ctx.get("risk_tier", ActionTier.TIER_0_READ_ONLY)
        if int(tier) >= int(ActionTier.TIER_2_EXTERNAL_IMPACT):
            return PolicyResult(
                effect="REQUIRE_APPROVAL",
                reason="Human approval required for real-world impact",
                metadata={"approval_required": True},
            )
        return None

    engine.register(deny_prod_secret_write)
    engine.register(require_human_for_high_risk)
    return engine
