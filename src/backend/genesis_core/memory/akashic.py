import subprocess
import hashlib
import json
import os
import time
from typing import List, Dict, Optional, Any

class AkashicRecords:
    """
    The Akashic Records: An immutable ledger of the system's life,
    anchored to the PanGenesis (Git) repository.

    Enhanced for Provenance and Causal Tracing.
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

    def append_record(self,
                      payload: Dict,
                      actor: str = "system",
                      intent_id: Optional[str] = None,
                      causal_link: Optional[str] = None) -> str:
        """
        Appends a new immutable record to the chain with provenance metadata.
        """
        with open(self.db_path, 'r+') as f:
            data = json.load(f)
            chain = data.get("chain", [])

            prev_hash = chain[-1]['hash'] if chain else "0" * 64
            timestamp = time.time()

            envelope = {
                "actor": actor,
                "intent_id": intent_id,
                "causal_link": causal_link,
                "data": payload
            }

            content = f"{timestamp}{json.dumps(envelope, sort_keys=True)}{prev_hash}".encode()
            curr_hash = hashlib.sha256(content).hexdigest()

            block = {
                "timestamp": timestamp,
                "provenance": {
                    "actor": actor,
                    "intent_id": intent_id,
                    "causal_link": causal_link
                },
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
                payload = block['payload']
                timestamp = block['timestamp']
                ph = block['prev_hash']
                prov = block.get('provenance', {})

                envelope = {
                    "actor": prov.get("actor", "system"),
                    "intent_id": prov.get("intent_id"),
                    "causal_link": prov.get("causal_link"),
                    "data": payload
                }

                content = f"{timestamp}{json.dumps(envelope, sort_keys=True)}{ph}".encode()
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

    def get_records(self, limit: int = 100, actor: Optional[str] = None) -> List[Dict]:
        """Retrieves records from the ledger, optionally filtered by actor."""
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            chain = data.get("chain", [])

            if actor:
                chain = [b for b in chain if b.get('provenance', {}).get('actor') == actor]

            return chain[-limit:]
        except Exception:
            return []

class MemoryProjectionManager:
    """
    Manages derived views of the Akashic Ledger.
    """
    def __init__(self, ledger: AkashicRecords):
        self.ledger = ledger

    def get_episodic_view(self, limit: int = 50) -> List[Dict]:
        records = self.ledger.get_records(limit=limit)
        timeline = []
        for r in records:
            prov = r.get('provenance', {})
            timeline.append({
                "time": r['timestamp'],
                "who": prov.get('actor', 'system'),
                "what": r['payload'].get('action') or r['payload'].get('type') or "Event",
                "details": r['payload'],
                "hash": r['hash'][:8]
            })
        return timeline

    def get_semantic_summary(self) -> Dict[str, Any]:
        records = self.ledger.get_records(limit=1000)
        summary = {
            "total_events": len(records),
            "actors": {},
            "recent_intents": []
        }
        for r in records:
            prov = r.get('provenance', {})
            actor = prov.get('actor', 'system')
            summary["actors"][actor] = summary["actors"].get(actor, 0) + 1
            if prov.get('intent_id'):
                summary["recent_intents"].append(prov['intent_id'])

        summary["recent_intents"] = list(set(summary["recent_intents"]))[-10:]
        return summary

class GitMemorySystem:
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path

    def _run_git(self, args: List[str]) -> str:
        try:
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
        if not self._run_git(["rev-parse", "--is-inside-work-tree"]):
            return False
        fsck = self._run_git(["fsck", "--no-dangling"])
        return "error" not in fsck.lower()

    def get_current_commit_hash(self) -> str:
        return self._run_git(["rev-parse", "HEAD"])
