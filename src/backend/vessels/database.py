from src.backend.genesis_core.protocol.schemas import AetherEvent
from src.backend.vessels.base import ActionPreview, DirectivePayload, ExecutionVessel


class DatabaseVessel(ExecutionVessel):
    def __init__(self):
        super().__init__(name="database")

    def _preview(self, envelope: AetherEvent, payload: DirectivePayload) -> ActionPreview:
        table = payload.params.get("table", "unknown")
        return ActionPreview(
            plan=f"Database adapter action {payload.action} on table {table}",
            diff=str(payload.params.get("patch", {}))[:120],
            tools=["database.client"],
            evidence={"transactional": True, "topic": envelope.topic},
        )

    def _execute(self, envelope: AetherEvent, payload: DirectivePayload) -> dict:
        return {"status": "dry_run", "action": payload.action, "table": payload.params.get("table")}
