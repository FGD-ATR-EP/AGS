import os
import shutil
from typing import Dict, Any, List
from src.backend.genesis_core.vessels.base import ExecutionVessel, ActionPreview
from src.backend.genesis_core.governance.core import ActionTier

class WorkspaceVessel(ExecutionVessel):
    """
    The Vessel for Document and File Operations.
    Restricted to a specific root directory (The Workspace).
    """
    def __init__(self, workspace_root: str = "workspace"):
        super().__init__(name="WorkspaceVessel", domain="files")
        self.root = os.path.abspath(workspace_root)
        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def _safe_path(self, relative_path: str) -> str:
        """Ensures the path is inside the workspace root."""
        full_path = os.path.abspath(os.path.join(self.root, relative_path))
        if not full_path.startswith(self.root):
            raise PermissionError(f"Access denied: {relative_path} is outside workspace.")
        return full_path

    async def simulate(self, action: str, params: Dict) -> ActionPreview:
        path = params.get("path", "unknown")

        if action == "write_file":
            content = params.get("content", "")
            exists = os.path.exists(self._safe_path(path))
            summary = f"{'Update' if exists else 'Create'} file: {path}"
            impact = f"Writing {len(content)} bytes to {path}."
            diff = f"+ {content[:50]}..." if not exists else "Existing content will be overwritten."
            return ActionPreview(summary=summary, impact=impact, risk_tier=ActionTier.TIER_1_REVERSIBLE_LOW_RISK, diff=diff)

        if action == "delete_file":
            summary = f"Delete file: {path}"
            impact = "Irreversible removal of the specified file."
            return ActionPreview(summary=summary, impact=impact, risk_tier=ActionTier.TIER_3_SENSITIVE_IRREVERSIBLE)

        return ActionPreview(summary=f"Unknown action: {action}", impact="None", risk_tier=ActionTier.TIER_0_READ_ONLY)

    async def execute(self, action: str, params: Dict) -> Dict[str, Any]:
        path = self._safe_path(params.get("path"))

        if action == "write_file":
            content = params.get("content", "")
            with open(path, 'w') as f:
                f.write(content)
            return {"status": "success", "file": path, "bytes": len(content)}

        if action == "read_file":
            if not os.path.exists(path):
                return {"status": "error", "message": "File not found"}
            with open(path, 'r') as f:
                content = f.read()
            return {"status": "success", "content": content}

        if action == "delete_file":
            if os.path.exists(path):
                os.remove(path)
                return {"status": "success", "message": "File deleted"}
            return {"status": "error", "message": "File not found"}

        raise ValueError(f"Action {action} not supported by WorkspaceVessel")
