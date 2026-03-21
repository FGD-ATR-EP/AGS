import json
import os
from typing import Any, Dict, List


class GemRepository:
    def __init__(self, path: str = "data/memory/gems/repository.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"gems": []}, handle, indent=2)

    def add(self, gem: Dict[str, Any]) -> Dict[str, Any]:
        with open(self.path, "r+", encoding="utf-8") as handle:
            data = json.load(handle)
            data["gems"].append(gem)
            handle.seek(0)
            json.dump(data, handle, indent=2)
            handle.truncate()
        return gem

    def list(self) -> List[Dict[str, Any]]:
        with open(self.path, "r", encoding="utf-8") as handle:
            return json.load(handle).get("gems", [])
