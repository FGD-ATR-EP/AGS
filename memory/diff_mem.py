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

diff_mem = DiffMem()
