import json
import os
from pathlib import Path
from typing import Any, Dict


class MemoryFabric:
    """Builds multiple memory projections from Akashic canonical event stream."""

    def __init__(self, ledger_path: str = "data/akashic_records.json", memory_root: str = "data/memory"):
        self.ledger_path = ledger_path
        self.memory_root = Path(memory_root)
        self.targets = {
            "episodic": self.memory_root / "episodes",
            "semantic": self.memory_root / "semantic",
            "procedural": self.memory_root / "procedures",
            "reflective": self.memory_root / "gems",
            "identity": self.memory_root / "identity",
        }
        for folder in self.targets.values():
            folder.mkdir(parents=True, exist_ok=True)

    def project(self) -> Dict[str, int]:
        if not os.path.exists(self.ledger_path):
            return {key: 0 for key in self.targets}

        with open(self.ledger_path, "r", encoding="utf-8") as handle:
            chain = json.load(handle).get("chain", [])

        counts = {key: 0 for key in self.targets}
        for block in chain:
            payload = block.get("payload", {})
            provenance = block.get("provenance", {})
            memory_type = self._infer_type(payload)
            counts[memory_type] += 1

            entry = {
                "hash": block.get("hash"),
                "timestamp": block.get("timestamp"),
                "payload": payload,
                "provenance": provenance,
                "correlation": block.get("correlation") or provenance.get("correlation") or payload.get("correlation") or {},
            }
            out_file = self.targets[memory_type] / f"{block.get('hash', 'event')}.json"
            with open(out_file, "w", encoding="utf-8") as write_handle:
                json.dump(entry, write_handle, indent=2)

        return counts

    def _infer_type(self, payload: Dict[str, Any]) -> str:
        event_type = str(payload.get("type", payload.get("action", "event"))).lower()
        if any(k in event_type for k in ("intent", "action", "outcome", "episode")):
            return "episodic"
        if any(k in event_type for k in ("summary", "semantic", "concept")):
            return "semantic"
        if any(k in event_type for k in ("procedure", "runbook", "playbook")):
            return "procedural"
        if any(k in event_type for k in ("gem", "reflection", "lesson")):
            return "reflective"
        return "identity"
