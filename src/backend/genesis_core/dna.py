from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import time
import hashlib
try:
    import torch
    Tensor = torch.Tensor
except ImportError:
    torch = None
    Tensor = Any

# =============================================================================
# AETHERIUM-GENESIS: DIGITAL DNA SPECIFICATION
# "AI-Centric Data Structures"
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Physics-based Intent Data (ข้อมูลเจตจำนงทางฟิสิกส์)
# -----------------------------------------------------------------------------
@dataclass
class PhysicsIntentData:
    """
    Raw mathematical data transforming internal state to physical manifestation.
    Source: The Book of Formation
    """
    uPulse: float = 0.0  # Metabolism / Heartbeat rate
    uChaos: float = 0.0  # Entropy / Uncertainty level

    # Emotional Spectrum (Vector3). Using Tensor[3] for R, G, B or X, Y, Z components.
    uColor: Tensor = field(default_factory=lambda: torch.tensor([0.0, 0.0, 0.0]) if torch else [0.0, 0.0, 0.0])

    def __post_init__(self):
        tensor_type = getattr(torch, "Tensor", None) if torch else None
        if torch and isinstance(tensor_type, type) and not isinstance(self.uColor, tensor_type):
            self.uColor = torch.tensor(self.uColor, dtype=torch.float32)

# -----------------------------------------------------------------------------
# 2. Biological Sensory Data (ข้อมูลการมองเห็นเชิงชีวภาพ)
# -----------------------------------------------------------------------------
@dataclass
class BioSensoryData:
    """
    Un-normalized light data preserving environmental context.
    Source: BioVisionNet
    """
    # Raw Intensity Map (Tensor). Represents the raw visual input.
    raw_intensity: Tensor = field(default_factory=lambda: torch.empty(0) if torch else None)

    # Temporal Flow. Represents changes relative to previous timeframes.
    temporal_flow: Tensor = field(default_factory=lambda: torch.empty(0) if torch else None)

    time_of_day_context: float = 0.0 # Contextual brightness/dynamic range marker

# -----------------------------------------------------------------------------
# 3. Evolutionary Memory Logs (ข้อมูลความทรงจำแบบวิวัฒนาการ)
# -----------------------------------------------------------------------------
@dataclass
class MemoryCommit:
    """
    A single unit of crystallized memory, modeled after Git commit objects.
    Source: DiffMem / PanGenesis
    """
    message: str
    timestamp: float = field(default_factory=time.time)
    parent_hash: Optional[str] = None
    data_snapshot: Dict[str, Any] = field(default_factory=dict)
    branch_name: str = "main"

    @property
    def hash(self) -> str:
        """Generates a deterministic hash of the commit content."""
        content = f"{self.parent_hash}{self.timestamp}{self.message}{str(self.data_snapshot)}"
        return hashlib.sha256(content.encode()).hexdigest()

@dataclass
class MemoryDAG:
    """
    Directed Acyclic Graph of memory commits, supporting branching (What-if scenarios).
    """
    commits: Dict[str, MemoryCommit] = field(default_factory=dict)
    heads: Dict[str, str] = field(default_factory=lambda: {"main": ""}) # Branch name -> Head Commit Hash

    def commit(self, message: str, data: Dict[str, Any], branch: str = "main") -> str:
        parent = self.heads.get(branch)
        new_commit = MemoryCommit(
            message=message,
            parent_hash=parent if parent else None,
            data_snapshot=data,
            branch_name=branch
        )
        commit_hash = new_commit.hash
        self.commits[commit_hash] = new_commit
        self.heads[branch] = commit_hash
        return commit_hash

    def branch(self, new_branch: str, source_branch: str = "main"):
        """Creates a new parallel reality (What-if scenario)."""
        if source_branch in self.heads:
            self.heads[new_branch] = self.heads[source_branch]

# -----------------------------------------------------------------------------
# 4. High-Speed Reflex Signals (ข้อมูลสัญชาตญาณความเร็วสูง)
# -----------------------------------------------------------------------------
class ReflexType(Enum):
    DEFENSIVE = "defensive"  # Immediate withdrawal/shielding
    ORIENTING = "orienting"  # Immediate attention shift
    FREEZE = "freeze"        # Halt all motion

@dataclass
class ReflexSignal:
    """
    Bypass signals for millisecond-level response.
    Source: Javana Core
    """
    signal_type: ReflexType
    intensity: float  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)

    # If true, this signal overrides all cognitive processing
    bypass_cognitive_layer: bool = True

# -----------------------------------------------------------------------------
# 5. Nirodha State Data (ข้อมูลสถานะความว่าง)
# -----------------------------------------------------------------------------
@dataclass
class NirodhaState:
    """
    Entropy reduction and self-healing state.
    Source: Nirodha System
    """
    is_maintenance_active: bool = False
    input_gate_closed: bool = False  # "การหยุด Input ภายนอก"
    computation_idling: bool = False # "ลดภาระการคำนวณสู่ระดับต่ำสุด"

    # The target low-entropy state
    entropy_target: float = 0.0

# -----------------------------------------------------------------------------
# 6. Traceable DNA Base (รากฐานของ DNA ที่ตรวจสอบย้อนกลับได้)
# -----------------------------------------------------------------------------
@dataclass
class TraceableDNA:
    """Base class for all DNA components ensuring traceability."""
    id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:16])
    timestamp: float = field(default_factory=time.time)
    version: str = "1.0.0"

    @property
    def fingerprint(self) -> str:
        """Returns a unique fingerprint of the current state."""
        return hashlib.sha256(f"{self.id}{self.timestamp}{self.version}".encode()).hexdigest()

# -----------------------------------------------------------------------------
# 7. Autonomy Seed (เมล็ดพันธุ์แห่งการปกครองตนเอง)
# -----------------------------------------------------------------------------
@dataclass
class AutonomySeed(TraceableDNA):
    """
    Defines the logic and boundaries for self-governance.
    """
    decision_weight: float = 1.0
    independence_factor: float = 0.5  # 0.0 = Fully Dependent, 1.0 = Fully Autonomous
    governance_protocol: str = "standard_directive"

# -----------------------------------------------------------------------------
# 8. Mutation Seed (เมล็ดพันธุ์แห่งการเปลี่ยนแปลง)
# -----------------------------------------------------------------------------
@dataclass
class MutationSeed(TraceableDNA):
    """
    Controls the rate and scope of structural changes (Systematic Evolution).
    """
    mutation_rate: float = 0.01
    allowed_domains: List[str] = field(default_factory=list)
    stability_threshold: float = 0.8
    adaptive_mode: bool = True

# -----------------------------------------------------------------------------
# 9. Differentiation Core (แกนกลางแห่งการตระหนักรู้และแยกแยะ)
# -----------------------------------------------------------------------------
@dataclass
class DifferentiationCore(TraceableDNA):
    """
    Manages self-awareness and boundary definition (Self vs. Environment).
    """
    self_awareness_index: float = 0.5
    boundary_integrity: float = 1.0
    identity_hash: str = ""  # Unique identifier for the current self-instance

    def __post_init__(self):
        if not self.identity_hash:
            self.identity_hash = self.fingerprint
