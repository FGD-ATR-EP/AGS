from src.backend.genesis_core.protocol.schemas import AetherEvent
from src.backend.vessels.base import ActionPreview, DirectivePayload, ExecutionVessel


class DriveVessel(ExecutionVessel):
    """Adapter boundary for remote drive providers."""

    def __init__(self):
        super().__init__(name="drive")

    def _preview(self, envelope: AetherEvent, payload: DirectivePayload) -> ActionPreview:
        return ActionPreview(
            plan=f"Drive adapter action {payload.action} on {payload.params.get('doc_id', 'new_doc')}",
            diff=str(payload.params.get("content", ""))[:120],
            tools=["drive.api"],
            evidence={"provider": payload.params.get("provider", "generic"), "topic": envelope.topic},
        )

    def _execute(self, envelope: AetherEvent, payload: DirectivePayload) -> dict:
        return {
            "status": "draft_only",
            "action": payload.action,
            "message": "Drive adapter pending provider binding",
        }
