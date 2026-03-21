from typing import Dict, Any, Optional
from datetime import datetime
from src.backend.genesis_core.models.visual import (
    EmbodimentContract, VisualParameters, VisualSpecifics,
    IntentCategory, BaseShape, ContractIntentCategory, TemporalPhase
)

class EmbodimentAdapter:
    """The Nervous System: Translates Cognitive Contracts into Visual Parameters.

    Implements the 'Application Binary Interface (ABI) of Cognition', converting
    high-level semantic intent into low-level physics and rendering parameters.
    """

    def translate(self, contract: EmbodimentContract) -> VisualParameters:
        """Converts an EmbodimentContract into VisualParameters.

        Applies the laws of cognitive physics (Conservation of Energy,
        Visibility of Entropy, Topology of Intent) to map abstract thought
        into concrete visual properties.

        Args:
            contract: The high-level intent contract from the interpreter.

        Returns:
            A VisualParameters object compatible with the frontend renderer.
        """

        # --- LAW 1: Conservation of Energy (Inertia) ---
        # High cognitive.effort = Slower, heavier particle movement (High Mass).
        # Low cognitive.effort = Fast, erratic, light movement (Low Mass).
        # We map 'effort' (0.0-1.0) to inverse energy/velocity.
        # However, purely low energy might look 'dead'.
        # So we map Effort -> Density (Mass) and keep Energy for Urgency.

        # Actually, let's follow the contract draft logic:
        # "If effort is high, velocity drops".
        # In VisualParameters, we use 'energy_level' as a proxy for general activity.
        effort = contract.cognitive.effort
        # Base energy is inverse of effort (Thinking hard = Stillness/Focus)
        energy_level = 1.0 - (effort * 0.6)

        # --- LAW 2: Visibility of Entropy (Turbulence) ---
        # High cognitive.uncertainty = Increased turbulence.
        uncertainty = contract.cognitive.uncertainty
        turbulence = uncertainty * 1.5 # Scale up to make it visible
        if turbulence > 1.0: turbulence = 1.0

        # --- LAW 3: Topology of Intent (Shape Polyfill) ---
        # Map new semantic shapes to existing GunUI primitives.
        contract_category = contract.intent.category

        base_shape = BaseShape.CLOUD # Default
        target_intent_category = IntentCategory.CHAT # Default

        if contract_category == ContractIntentCategory.ANALYTIC:
            # Contract: HEXAGON -> GunUI: CUBE
            base_shape = BaseShape.CUBE
            target_intent_category = IntentCategory.CHAT

        elif contract_category == ContractIntentCategory.CREATIVE:
            # Contract: NEBULA -> GunUI: CLOUD (or VORTEX)
            base_shape = BaseShape.CLOUD
            target_intent_category = IntentCategory.CHAT

        elif contract_category == ContractIntentCategory.SYSTEM_OPS:
            # Contract: GRID -> GunUI: CUBE (Force Alignment)
            # Or use SCATTER for raw data
            base_shape = BaseShape.CUBE # Grid-like
            target_intent_category = IntentCategory.COMMAND

        elif contract_category == ContractIntentCategory.CHIT_CHAT:
            base_shape = BaseShape.SPHERE
            target_intent_category = IntentCategory.CHAT

        # Temporal Overrides
        if contract.temporal_state.phase == TemporalPhase.THINKING:
            return self.get_temporal_visuals(TemporalPhase.THINKING)

        # Color Logic (Derived from Intent/Sentiment)
        # We don't have explicit color in Contract yet, use Sentiment or hardcode map
        color = "#FFFFFF"
        if contract_category == ContractIntentCategory.ANALYTIC:
            color = "#00FFFF" # Cyan
        elif contract_category == ContractIntentCategory.CREATIVE:
            color = "#FF00FF" # Magenta
        elif contract_category == ContractIntentCategory.SYSTEM_OPS:
            color = "#00FF00" # Green

        # Emotional Valence (Derived or default)
        valence = 0.0

        return VisualParameters(
            intent_category=target_intent_category,
            emotional_valence=valence,
            energy_level=energy_level,
            semantic_concepts=[],
            visual_parameters=VisualSpecifics(
                base_shape=base_shape,
                turbulence=turbulence,
                particle_density=0.5 + (effort * 0.4), # High effort = High density
                color_palette=color,
                flow_direction="none"
            )
        )

    def get_temporal_visuals(self, phase: TemporalPhase) -> VisualParameters:
        """Generates immediate visual states for specific temporal phases.

        Used to provide instant feedback (e.g., "Thinking") before the LLM processing completes,
        reducing perceived latency.

        Args:
            phase: The requested TemporalPhase (e.g., THINKING, LISTENING).

        Returns:
            A VisualParameters object pre-configured for the requested phase.
        """
        if phase == TemporalPhase.THINKING:
            # High Velocity + Center Focus (Vortex)
            return VisualParameters(
                intent_category=IntentCategory.CHAT,
                emotional_valence=0.1,
                energy_level=0.9, # High Energy
                semantic_concepts=["processing", "loading"],
                visual_parameters=VisualSpecifics(
                    base_shape=BaseShape.VORTEX,
                    turbulence=0.8, # High Entropy/Thinking
                    particle_density=0.8,
                    color_palette="#FFA500", # Orange/Gold for active thought
                    flow_direction="inward"
                )
            )

        elif phase == TemporalPhase.LISTENING:
            return VisualParameters(
                intent_category=IntentCategory.CHAT,
                emotional_valence=0.0,
                energy_level=0.3,
                semantic_concepts=["listening"],
                visual_parameters=VisualSpecifics(
                    base_shape=BaseShape.SPHERE,
                    turbulence=0.1,
                    particle_density=0.3,
                    color_palette="#FFFFFF",
                    flow_direction="none"
                )
            )

        # Default fallback
        return VisualParameters(
            intent_category=IntentCategory.CHAT,
            emotional_valence=0.0,
            energy_level=0.1,
            semantic_concepts=[],
            visual_parameters=VisualSpecifics(
                base_shape=BaseShape.CLOUD,
                turbulence=0.0,
                particle_density=0.1,
                color_palette="#888888",
                flow_direction="none"
            )
        )
