import logging
from typing import Dict, Any, Union
from datetime import datetime
from src.backend.genesis_core.models.visual import (
    VisualParameters, IntentCategory, BaseShape,
    EmbodimentContract, TemporalState, CognitiveMetadata, IntentData,
    TemporalPhase, ContractIntentCategory
)

logger = logging.getLogger("Verifier")

class VisualVerifier:
    """Ensures data integrity for visual and embodiment schemas.

    Performs validation, clamping, and repair of data structures to prevent
    runtime errors in the rendering engine.
    """

    @staticmethod
    def verify_contract(data: Union[Dict[str, Any], EmbodimentContract]) -> EmbodimentContract:
        """Validates the input data against the EmbodimentContract schema.

        If validation fails, attempts to repair the data structure using default values.

        Args:
            data: A dictionary or EmbodimentContract instance to verify.

        Returns:
            A valid EmbodimentContract instance.
        """
        if isinstance(data, EmbodimentContract):
            return data

        try:
            return EmbodimentContract(**data)
        except Exception as e:
            logger.warning(f"Strict contract validation failed: {e}. Attempting repair.")
            return VisualVerifier._repair_contract(data)

    @staticmethod
    def _repair_contract(data: Dict[str, Any]) -> EmbodimentContract:
        """Repairs malformed contract data with safe defaults.

        Args:
            data: The potentially malformed data dictionary.

        Returns:
            A sanitized EmbodimentContract.
        """
        # Defaults
        default_phase = TemporalPhase.MANIFESTING
        default_category = ContractIntentCategory.CHIT_CHAT

        # 1. Temporal State
        ts = data.get("temporal_state", {})
        if not isinstance(ts, dict): ts = {}

        phase_str = str(ts.get("phase", "MANIFESTING")).upper()
        if phase_str not in [e.value for e in TemporalPhase]:
            phase_str = TemporalPhase.MANIFESTING.value

        ts["phase"] = phase_str
        ts["stability"] = max(0.0, min(float(ts.get("stability", 0.5)), 1.0))
        ts["duration_ms"] = int(ts.get("duration_ms", 0))

        # 2. Cognitive Metadata
        cog = data.get("cognitive", {})
        if not isinstance(cog, dict): cog = {}

        cog["effort"] = max(0.0, min(float(cog.get("effort", 0.5)), 1.0))
        cog["uncertainty"] = max(0.0, min(float(cog.get("uncertainty", 0.1)), 1.0))
        cog["latency_factor"] = max(0.0, min(float(cog.get("latency_factor", 0.0)), 1.0))

        # 3. Intent Data
        in_data = data.get("intent", {})
        if not isinstance(in_data, dict): in_data = {}

        cat_str = str(in_data.get("category", "CHIT_CHAT")).upper()
        # Map old categories if present
        if "CHAT" in cat_str and "CHIT" not in cat_str: cat_str = "CHIT_CHAT"
        if "REQUEST" in cat_str: cat_str = "ANALYTIC" # Map request to analytic?
        if cat_str not in [e.value for e in ContractIntentCategory]:
             cat_str = ContractIntentCategory.CHIT_CHAT.value

        in_data["category"] = cat_str
        in_data["purity"] = max(0.0, min(float(in_data.get("purity", 0.9)), 1.0))

        # Reconstruct
        repaired_data = {
            "contract_version": data.get("contract_version", "1.0"),
            "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
            "temporal_state": ts,
            "cognitive": cog,
            "intent": in_data,
            "text_content": data.get("text_content")
        }

        try:
            return EmbodimentContract(**repaired_data)
        except Exception as e:
            logger.error(f"Contract repair failed: {e}. Returning safe default.")
            # Absolute fallback
            return EmbodimentContract(
                temporal_state=TemporalState(phase=TemporalPhase.ERROR, stability=0.0),
                cognitive=CognitiveMetadata(effort=0.0, uncertainty=1.0),
                intent=IntentData(category=ContractIntentCategory.SYSTEM_OPS, purity=0.0),
                text_content="System Error: Contract Violation"
            )

    @staticmethod
    def verify_and_repair(data: Union[Dict[str, Any], VisualParameters]) -> VisualParameters:
        """Validates the input data against the VisualParameters schema.

        If strict validation fails, attempts to repair common issues (e.g., incorrect enums,
        out-of-bounds numbers) or returns a safe default.

        Args:
            data: A dictionary or VisualParameters instance to verify.

        Returns:
            A valid VisualParameters instance.
        """
        if isinstance(data, VisualParameters):
            return data

        try:
            # 1. Attempt strict parsing
            return VisualParameters(**data)
        except Exception as e:
            logger.warning(f"Strict validation failed: {e}. Attempting repair.")
            return VisualVerifier._repair(data)

    @staticmethod
    def _repair(data: Dict[str, Any]) -> VisualParameters:
        """Repairs malformed visual parameter data.

        Handles enum mapping, value clamping, and missing fields.

        Args:
            data: The potentially malformed data dictionary.

        Returns:
            A sanitized VisualParameters instance.
        """
        # Fallback values
        safe_defaults = {
            "intent_category": IntentCategory.CHAT,
            "emotional_valence": 0.0,
            "energy_level": 0.5,
            "semantic_concepts": [],
            "visual_parameters": {
                "base_shape": BaseShape.CLOUD,
                "turbulence": 0.1,
                "particle_density": 0.5,
                "color_palette": "#FFFFFF",
                "flow_direction": "none"
            }
        }

        # 1. Fix Intent Category
        raw_cat = str(data.get("intent_category", "")).lower()
        if raw_cat not in [e.value for e in IntentCategory]:
            # Map common mistakes
            if "ask" in raw_cat or "question" in raw_cat:
                data["intent_category"] = IntentCategory.REQUEST
            elif "do" in raw_cat or "make" in raw_cat:
                data["intent_category"] = IntentCategory.COMMAND
            elif "error" in raw_cat or "fail" in raw_cat:
                data["intent_category"] = IntentCategory.ERROR
            else:
                data["intent_category"] = IntentCategory.CHAT

        # 2. Clamp Numeric Values
        def clamp(val, min_v, max_v):
            try:
                v = float(val)
                return max(min_v, min(v, max_v))
            except:
                return (min_v + max_v) / 2

        data["emotional_valence"] = clamp(data.get("emotional_valence", 0.0), -1.0, 1.0)
        data["energy_level"] = clamp(data.get("energy_level", 0.5), 0.0, 1.0)

        # 3. Fix Visual Parameters
        vp = data.get("visual_parameters", {})
        if not isinstance(vp, dict):
            vp = safe_defaults["visual_parameters"]

        # Base Shape
        raw_shape = str(vp.get("base_shape", "")).lower()
        valid_shapes = [e.value for e in BaseShape]
        if raw_shape not in valid_shapes:
            # Heuristic mapping
            if "round" in raw_shape or "ball" in raw_shape:
                vp["base_shape"] = BaseShape.SPHERE
            elif "box" in raw_shape or "square" in raw_shape:
                vp["base_shape"] = BaseShape.CUBE
            elif "spin" in raw_shape or "swirl" in raw_shape:
                vp["base_shape"] = BaseShape.VORTEX
            elif "break" in raw_shape or "crack" in raw_shape:
                vp["base_shape"] = BaseShape.CRACKS
            else:
                vp["base_shape"] = BaseShape.CLOUD

        # Clamp visual numerics
        vp["turbulence"] = clamp(vp.get("turbulence", 0.1), 0.0, 1.0)
        vp["particle_density"] = clamp(vp.get("particle_density", 0.5), 0.0, 1.0)

        # Color (Naive check)
        color = str(vp.get("color_palette", "#FFFFFF"))
        if not color.startswith("#"):
            vp["color_palette"] = "#FFFFFF" # Default to white if invalid

        data["visual_parameters"] = vp

        # Final try
        try:
            return VisualParameters(**data)
        except Exception as e:
            logger.error(f"Repair failed: {e}. Returning safe default.")
            return VisualParameters(**safe_defaults)
