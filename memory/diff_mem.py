import os
import subprocess
import logging
from typing import Optional, Dict, List, Any
import json
from datetime import datetime

logger = logging.getLogger("DiffMem")

class DiffMem:
    """
    Git-based Long-term Memory.
    Uses a Git repository to store and track the evolution of 'Gems of Wisdom'.
    """
    def __init__(self, repo_path: str = "d:/AETHERIUM GENESIS/memory_repo"):
        self.repo_path = repo_path
        self._ensure_repo()

    def _ensure_repo(self):
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            self._run_git("init")
            logger.info(f"[DiffMem] Initialized Memory Repository at {self.repo_path}")

    def _run_git(self, *args) -> str:
        cmd = ["git"] + list(args)
        result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"[DiffMem] Git Error: {result.stderr}")
            return ""
        return result.stdout.strip()

    def commit_gem(self, filename: str, content: Dict[str, Any], message: str):
        """
        Saves a Gem as a JSON file and commits it to Git.
        """
        full_path = os.path.join(self.repo_path, filename)
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
            
        self._run_git("add", filename)
        self._run_git("commit", "-m", message)
        logger.info(f"[DiffMem] Committed Gem: {filename} - {message}")

    def get_evolution(self, filename: str) -> List[str]:
        """
        Retrieves the history of a specific Gem.
        """
        log = self._run_git("log", "--pretty=format:%h - %s (%ci)", "--", filename)
        return log.split("\n") if log else []

    def query_akashic_ledger(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Query the Akashic ledger for replay console or ledgers.
        """
        log = self._run_git("log", "-n", "10", "--pretty=format:%h|%ci|%s")
        events = []
        if log:
            for line in log.split("\n"):
                parts = line.split("|")
                if len(parts) == 3:
                    events.append({"id": parts[0], "timestamp": parts[1], "summary": parts[2]})
        return events

    def get_intent_execution_diff(self, intent_id: str) -> Dict[str, Any]:
        """
        Fetch Plan, Approved, and Result components of an intent.
        """
        return {
            "intent_id": intent_id,
            "plan_payload": {"action": "unknown", "target": "System"},
            "approved_command": {"action": "unknown", "authorized_by": "Validator"},
            "actual_output": {"status": "mocked", "note": "Diff tracking enabled"}
        }

diff_mem = DiffMem()
