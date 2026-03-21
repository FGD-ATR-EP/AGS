from src.backend.genesis_core.memory.akashic import AkashicRecords, GitMemorySystem

class PanGenesisAuditor:
    def __init__(self, git_repo_path=".", akashic_db_path="data/akashic_records.json"):
        self.git = GitMemorySystem(git_repo_path)
        self.akashic = AkashicRecords(akashic_db_path)

    def audit_eternal_memory(self):
        """Audits the integrity of the eternal memory."""
        audit_results = {
            "type": "memory",
            "metrics": {
                "git_integrity": 1.0 if self.git.verify_integrity() else 0.0,
                "akashic_immutability": 1.0 if self.akashic.verify_hash_chain() else 0.0,
                "temporal_consistency": 1.0 if self.akashic.check_temporal_consistency() else 0.0,
            },
            "timestamp": None # To be filled by dashboard
        }

        # Check Soul Archives (Placeholder - assuming it's a directory check)
        audit_results["metrics"]["soul_archives_completeness"] = 1.0

        return audit_results
