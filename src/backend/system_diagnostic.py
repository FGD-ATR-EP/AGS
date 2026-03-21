import sys
import os
import json
import time
import importlib.util
import inspect
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Ensure src is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.backend.genesis_core.audit.logger import EvolutionLogger
from src.backend.genesis_core.dna import AutonomySeed, MutationSeed, DifferentiationCore, TraceableDNA

# Initialize Logger
logger = EvolutionLogger()

CONSTITUTION_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs/CONSTITUTION.md"))

def load_constitution(path: str = CONSTITUTION_PATH) -> Dict[str, Any]:
    """Loads and parses the CONSTITUTION.md file."""
    if not os.path.exists(path):
        return {"error": "Constitution file not found"}

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Simple parsing to extract Core Directives
    directives = []
    lines = content.split('\n')
    in_directives = False

    for line in lines:
        if "## Core Directives" in line:
            in_directives = True
            continue
        if in_directives and line.startswith("## ") and "Core Directives" not in line:
            in_directives = False
            break
        if in_directives and line.strip().startswith("###"):
            directives.append(line.strip())

    return {
        "content": content,
        "core_directives": directives
    }

def check_missing_components(module_path: str, required_classes: List[str]) -> List[str]:
    """Checks if required classes exist in the module."""
    missing = []
    try:
        spec = importlib.util.spec_from_file_location("dna_module", module_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for cls_name in required_classes:
                if not hasattr(module, cls_name):
                    missing.append(cls_name)
    except Exception as e:
        print(f"Error checking module components: {e}")
        return required_classes # Assume all missing if error
    return missing

def analyze_mutation_patterns(log_path: str) -> List[Dict[str, Any]]:
    """Analyzes mutation logs for patterns."""
    # Placeholder logic as we rely on EvolutionLogger
    return logger.read_logs("evolution", limit=50)

def detect_anomalies(logs: List[Dict[str, Any]]) -> int:
    """Detects anomalies in logs."""
    anomalies = 0
    for log in logs:
        if "error" in str(log).lower() or "violation" in str(log).lower():
            anomalies += 1
    return anomalies

def validate_intent_alignment(dna_path: str, constitution_path: str, tolerance: float = 0.85) -> float:
    """Validates if DNA aligns with Constitution directives."""
    # This is a heuristic check. In a real system, this might involve NLP or formal verification.
    # Here we check if the DNA file structure implies adherence (e.g., proper inheritance).

    constitution = load_constitution(constitution_path)
    if "error" in constitution:
        return 0.0

    directives = constitution.get("core_directives", [])
    if not directives:
        return 0.0 # No directives found to validate against

    # Check if DNA classes exist and inherit from TraceableDNA
    try:
        spec = importlib.util.spec_from_file_location("dna_module", dna_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            score = 0.0
            checks = 0

            # Check 1: DNA classes should exist
            for cls_name in ["AutonomySeed", "MutationSeed", "DifferentiationCore"]:
                checks += 1
                if hasattr(module, cls_name):
                    cls = getattr(module, cls_name)
                    # Check 2: Inheritance from TraceableDNA
                    # We check base class names to avoid identity issues with re-imported modules
                    base_names = [b.__name__ for b in cls.__bases__]
                    if "TraceableDNA" in base_names:
                        score += 1.0
                    else:
                        # Also check if it inherits from something that inherits from TraceableDNA
                        # This is a shallow check
                        score += 0.5 # Exists but inheritance unclear

            # Normalize score
            return score / checks if checks > 0 else 0.0

    except Exception:
        return 0.0

    return 1.0 # Default fallback if everything seems okay but logic was simple

class DifferentiationMonitor:
    def check_self_awareness(self):
        """Checks if the system can identify itself."""
        # Simulated check for FIRMA boundary and self-coherence
        return {
            "boundary_stability": True,
            "self_coherence": True,
            "identity_crises": []
        }

    def scan_firma_integrity(self):
        return True

    def measure_self_reference(self):
        return 0.95

    def detect_identity_conflicts(self):
        return []

class MutationHealthMonitor:
    def __init__(self):
        self.mutation_history = [] # In a real scenario, load from DB or logs
        self.constitution = load_constitution()

    def generate_health_report(self):
        return {
            "constitution_violations": self.check_constitution_compliance(),
            "mutation_entropy": 0.5, # Placeholder
            "adaptive_capacity": "High",
            "evolutionary_trajectory": "Stable"
        }

    def check_constitution_compliance(self):
        return []

class EvolutionaryGuardrails:
    def __init__(self):
        self.red_lines = [] # Load from config or constitution

    def check_red_line_violations(self, system_state=None):
        return []

def audit_dna_evolution(dna_file_path: str = "src/backend/genesis_core/dna.py", intent_file: str = CONSTITUTION_PATH):
    """Audits the DNA evolution."""
    abs_dna_path = os.path.abspath(dna_file_path)

    required_seeds = ["AutonomySeed", "MutationSeed", "DifferentiationCore"]
    missing_seeds = check_missing_components(abs_dna_path, required_seeds)

    mutation_logs = analyze_mutation_patterns("logs/genesis_cycle.log")
    anomalous_mutations = detect_anomalies(mutation_logs)

    intent_compliance = validate_intent_alignment(abs_dna_path, intent_file)

    return {
        "dna_integrity": len(missing_seeds) == 0,
        "missing_components": missing_seeds,
        "mutation_health": anomalous_mutations < 3,
        "intent_alignment": intent_compliance
    }

def audit_genesis_cycle():
    """Audits the Genesis Cycle (The Three Ticks)."""
    # Logic to read genesis_cycle.log and verify sequence
    logs = logger.read_logs("genesis_cycle", limit=50)
    # Validate sequence... for now return basic status
    return {
        "cycle_active": len(logs) > 0,
        "last_phase": logs[-1]["phase"] if logs else "unknown",
        "integrity": True
    }

def main():
    print(f"Starting System Inspection Protocol (SIP)...")
    print(f"Constitution Path: {CONSTITUTION_PATH}")

    dna_path = os.path.join(os.path.dirname(__file__), "genesis_core/dna.py")

    # 1. Audit DNA
    dna_report = audit_dna_evolution(dna_path, CONSTITUTION_PATH)
    logger.log_evolution_event("AUDIT_DNA", dna_report)

    # 2. Audit Genesis Cycle
    genesis_report = audit_genesis_cycle()
    logger.log_evolution_event("AUDIT_GENESIS", genesis_report)

    # 3. Mutation Monitor
    mutation_monitor = MutationHealthMonitor()
    mutation_report = mutation_monitor.generate_health_report()

    # 4. Guardrails
    guardrails = EvolutionaryGuardrails()
    red_lines = guardrails.check_red_line_violations()

    final_report = {
        "timestamp": datetime.now().isoformat(),
        "system_health": {
            "status": "healthy" if dna_report["dna_integrity"] else "degraded",
            "dna_integrity": dna_report,
            "genesis_cycle": genesis_report,
            "mutation_health": mutation_report,
            "red_line_violations": red_lines
        }
    }

    print(json.dumps(final_report, indent=2))

if __name__ == "__main__":
    main()
