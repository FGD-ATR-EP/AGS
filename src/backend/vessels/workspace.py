import os

from src.backend.genesis_core.protocol.schemas import AetherEvent
from src.backend.vessels.base import ActionPreview, DirectivePayload, ExecutionVessel


class WorkspaceVessel(ExecutionVessel):
    def __init__(self, workspace_root: str = "workspace_runtime"):
        super().__init__(name="workspace")
        self.root = os.path.abspath(workspace_root)
        os.makedirs(self.root, exist_ok=True)

    def _safe_path(self, path: str) -> str:
        resolved = os.path.abspath(os.path.join(self.root, path))
        if not resolved.startswith(self.root):
            raise PermissionError("Path escapes workspace sandbox")
        return resolved

    def _preview(self, envelope: AetherEvent, payload: DirectivePayload) -> ActionPreview:
        path = payload.params.get("path", "")
        if payload.action == "write_file":
            return ActionPreview(
                plan=f"Write file at {path}",
                diff=f"+ {str(payload.params.get('content', ''))[:80]}",
                tools=["workspace.fs"],
                evidence={"path": path, "topic": envelope.topic},
            )
        return ActionPreview(
            plan=f"Run workspace adapter action {payload.action}",
            diff="",
            tools=["workspace.fs"],
            evidence={"path": path, "topic": envelope.topic},
        )

    def _execute(self, envelope: AetherEvent, payload: DirectivePayload) -> dict:
        target = self._safe_path(payload.params.get("path", ""))
        if payload.action == "write_file":
            with open(target, "w", encoding="utf-8") as handle:
                handle.write(payload.params.get("content", ""))
            return {"status": "ok", "path": target}
        if payload.action == "read_file":
            with open(target, "r", encoding="utf-8") as handle:
                return {"status": "ok", "content": handle.read(), "path": target}
        raise ValueError(f"Unsupported workspace action: {payload.action}")
