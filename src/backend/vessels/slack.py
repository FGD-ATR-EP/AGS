from src.backend.genesis_core.protocol.schemas import AetherEvent
from src.backend.vessels.base import ActionPreview, DirectivePayload, ExecutionVessel


class SlackVessel(ExecutionVessel):
    def __init__(self):
        super().__init__(name="slack")

    def _preview(self, envelope: AetherEvent, payload: DirectivePayload) -> ActionPreview:
        channel = payload.params.get("channel", "#general")
        return ActionPreview(
            plan=f"Dispatch Slack adapter action {payload.action} to {channel}",
            diff=str(payload.params.get("text", ""))[:200],
            tools=["slack.api"],
            evidence={"mode": "draft", "topic": envelope.topic},
        )

    def _execute(self, envelope: AetherEvent, payload: DirectivePayload) -> dict:
        return {
            "status": "draft_only",
            "channel": payload.params.get("channel"),
            "action": payload.action,
        }
