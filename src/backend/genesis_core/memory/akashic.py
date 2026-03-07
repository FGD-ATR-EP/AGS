import subprocess
import hashlib
import json
import os
import time
from typing import List, Dict, Optional

class AkashicRecords:
    """
    The Akashic Records: An immutable ledger of the system's life,
    anchored to the PanGenesis (Git) repository.
    """
    def __init__(self, db_path: str = "data/akashic_records.json"):
        self.db_path = db_path
        self.ensure_db()

    def ensure_db(self):
        directory = os.path.dirname(self.db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({"chain": []}, f)

    def append_record(self, payload: Dict) -> str:
        """Appends a new immutable record to the chain."""
        with open(self.db_path, 'r+') as f:
            data = json.load(f)
            chain = data.get("chain", [])

            prev_hash = chain[-1]['hash'] if chain else "0" * 64
            timestamp = time.time()

            # Create Block
            content = f"{timestamp}{json.dumps(payload, sort_keys=True)}{prev_hash}".encode()
            curr_hash = hashlib.sha256(content).hexdigest()

            block = {
                "timestamp": timestamp,
                "payload": payload,
                "prev_hash": prev_hash,
                "hash": curr_hash
            }

            chain.append(block)

            f.seek(0)
            json.dump({"chain": chain}, f, indent=2)
            f.truncate()

            return curr_hash

    def verify_hash_chain(self) -> bool:
        """Verifies the cryptographic integrity of the local record chain."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)

            chain = data.get("chain", [])
            if not chain:
                return True

            prev_hash = "0" * 64
            for block in chain:
                # Recompute hash
                payload = block['payload']
                timestamp = block['timestamp']
                ph = block['prev_hash']

                if ph != prev_hash:
                    return False

                content = f"{timestamp}{json.dumps(payload, sort_keys=True)}{ph}".encode()
                curr_hash = hashlib.sha256(content).hexdigest()

                if curr_hash != block['hash']:
                    return False

                prev_hash = curr_hash

            return True
        except Exception:
            return False

    def check_temporal_consistency(self) -> bool:
        """Verifies that timestamps are monotonically increasing."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            chain = data.get("chain", [])

            last_ts = 0.0
            for block in chain:
                if block['timestamp'] < last_ts:
                    return False
                last_ts = block['timestamp']
            return True
        except Exception:
            return False

class GitMemorySystem:
    """
    Interface to the PanGenesis (Git) Repository.
    """
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def _run_git(self, args: List[str]) -> str:
        try:
            # Check if git exists
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    def verify_integrity(self) -> bool:
        """Checks if the git repository is healthy."""
        # Check if it is a git repo
        if not self._run_git(["rev-parse", "--is-inside-work-tree"]):
            return False

        # Run fsck to check for database corruption
        fsck = self._run_git(["fsck", "--no-dangling"])
        return "error" not in fsck.lower()

    def get_current_commit_hash(self) -> str:
        return self._run_git(["rev-parse", "HEAD"])
