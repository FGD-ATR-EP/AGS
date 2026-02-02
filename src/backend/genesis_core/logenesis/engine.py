import json
import os
import math
import re
from typing import Dict, Any, Optional, Tuple, Union
from datetime import datetime
from pydantic import ValidationError
import logging

from src.backend.genesis_core.models.logenesis import (
    LogenesisResponse, LogenesisState, IntentVector, ExpressionState,
    VisualQualia, AudioQualia, PhysicsParams, IntentPacket, StateMetrics
)
from src.backend.genesis_core.models.light import LightIntent, LightAction
from src.backend.departments.presentation.formation_manager import FormationManager
from src.backend.genesis_core.state.aether_state import AetherOutput, AetherState
from src.backend.genesis_core.lifecycle import LifecycleManager
from src.backend.genesis_core.models.intent import SystemIntent, IntentPayload, IntentContext

# New Imports
from src.backend.genesis_core.models.visual import VisualParameters, IntentCategory, BaseShape, VisualSpecifics, EmbodimentContract
from .embodiment import EmbodimentAdapter
from src.backend.core.config import settings

logger = logging.getLogger("LogenesisEngine")

class StateStore:
    """Persistence layer for Logenesis expression states.

    Manages the saving and loading of session-specific state data (inertia, velocity, current vector)
    to a local JSON file.
    """
    def __init__(self, filepath: str = "logenesis_state.json"):
        """Initializes the StateStore.

        Args:
            filepath: Path to the JSON file for state persistence.
        """
        self.filepath = filepath
        self._cache: Dict[str, ExpressionState] = {}
        self._load()

    def _load(self):
        """Loads states from disk into memory."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                for sid, state_dict in data.items():
                    try:
                        self._cache[sid] = ExpressionState(**state_dict)
                    except ValidationError:
                        continue # Skip invalid entries
        except Exception as e:
            logger.error(f"Error loading state store: {e}")

    def save(self):
        """Saves current memory states to disk."""
        try:
            data = {sid: state.model_dump(mode='json') for sid, state in self._cache.items()}
            with open(self.filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state store: {e}")

    def get_state(self, session_id: str) -> ExpressionState:
        """Retrieves or initializes the state for a given session.

        Args:
            session_id: The unique session identifier.

        Returns:
            The ExpressionState object.
        """
        if session_id not in self._cache:
            # Initialize with default neutral state
            default_vector = IntentVector(
                epistemic_need=0.1,
                subjective_weight=0.1,
                decision_urgency=0.1,
                precision_required=0.1
            )
            self._cache[session_id] = ExpressionState(
                current_vector=default_vector,
                velocity=0.0,
                inertia=0.8
            )
        return self._cache[session_id]

    def update_state(self, session_id: str, state: ExpressionState):
        """Updates and persists the state for a session.

        Args:
            session_id: The unique session identifier.
            state: The new ExpressionState.
        """
        self._cache[session_id] = state
        self.save() # Naive save on every update for now

class LogenesisEngine:
    """The Cognitive Fabric Implementation (Refactored for Distributed Agents).

    This engine acts as the core reasoning substrate for the Cognitive Infrastructure.
    It manages the transition between 'Nirodha' (Stillness) and 'Awakened' (Active Processing)
    states.

    REFACTOR NOTICE: Cognitive Interpretation is now offloaded to AgioSage Agent via LifecycleManager.
    This class now focuses on State Drift, Physics, and Orchestration.
    """
    def __init__(self):
        """Initializes the engine, managers, adapters."""
        self.state = LogenesisState.VOID
        self.state_store = StateStore()
        self.formation_manager = FormationManager()
        self.adapter = EmbodimentAdapter()

        # Lifecycle Manager (The K3s Simulator)
        self.lifecycle = LifecycleManager()

    async def startup(self):
        """Initializes the distributed agent system."""
        await self.lifecycle.startup()

    async def shutdown(self):
        """Shuts down the distributed agent system."""
        await self.lifecycle.shutdown()

    async def process(self, packet: Union[IntentPacket, str], session_id: str = "global", memory_index: Optional[list] = None, recalled_context: Optional[str] = None) -> LogenesisResponse:
        """Processes an incoming intent packet and generates a cognitive response.

        This method orchestrates the full cognitive cycle:
        1. Normalization of input.
        2. Intent Interpretation (via AgioSage Agent).
        3. Embodiment Adaptation (Translation to Visuals).
        4. State Drift Calculation (Physics of Thought).
        5. Manifestation Gating (Deciding to show visuals).
        6. Response Synthesis.

        Args:
            packet: The input data, either a raw string or an IntentPacket.
            session_id: The session identifier for state persistence.
            memory_index: Optional list of memory items for recall checks.
            recalled_context: Optional string of previously recalled context.

        Returns:
            A LogenesisResponse containing text, visual params, and system state.
        """
        # 0. Packet Normalization
        if isinstance(packet, str):
            packet = IntentPacket(
                modality="text",
                embedding=None,
                energy_level=0.5,
                confidence=1.0,
                raw_payload=packet
            )

        text = ""
        if packet.modality == "text":
            text = packet.raw_payload
            # Check for Nirodha Triggers (The "Silence Protocol")
            if any(w in text.lower() for w in ["sleep", "stop", "rest", "retreat", "bye", "enough", "พอ", "พัก"]):
                return self.enter_nirodha()

        # If currently in VOID or NIRODHA, wake up
        if self.state != LogenesisState.AWAKENED:
            self.state = LogenesisState.AWAKENED

        contract = None
        visual_params = None
        input_intent = None

        if packet.modality == "text":
            # 1. Intent Interpretation (The "Cognitive Cycle")
            # Returns EmbodimentContract (High Level) from AgioSage Agent

            # Construct SystemIntent for the Bus
            query_intent = SystemIntent(
                origin_agent="LogenesisEngine",
                target_agent="AgioSage_v1",
                intent_type="COGNITIVE_QUERY",
                payload=IntentPayload(content=text, modality="text"),
                context=IntentContext(energy_level=packet.energy_level, emotional_valence=0.0)
            )

            # Request processing via Lifecycle
            response_intent = await self.lifecycle.process_request(query_intent)

            if response_intent and response_intent.intent_type == "COGNITIVE_RESPONSE":
                try:
                    # Deserialize contract
                    contract_data = response_intent.payload.content
                    contract = EmbodimentContract(**contract_data)
                except Exception as e:
                    logger.error(f"Failed to parse EmbodimentContract from AgioSage: {e}")
            else:
                logger.warning("AgioSage failed to respond. Using empty contract.")
                # Fallback to keep system alive
                contract = EmbodimentContract(
                    temporal_state={"phase": "ERROR", "stability": 0.0},
                    cognitive={"effort": 0.0, "uncertainty": 1.0},
                    intent={"category": "SYSTEM_OPS", "purity": 0.0},
                    text_content="[System Error: Cognitive Core Unreachable]"
                )

            # 1.5 Adaptation (The "Nervous System")
            # Translates Contract -> VisualParameters (Low Level)
            visual_params = self.adapter.translate(contract)

            # Map New VisualParameters to Old IntentVector for Physics/Drift Logic
            input_intent = self._map_visual_to_intent_vector(visual_params)

        elif packet.modality == "visual":
             # Visual Path
             input_intent = self._map_visual_packet_to_intent(packet)
             # Derive visual params from AetherOutput
             if isinstance(packet.raw_payload, AetherOutput):
                 visual_params = self._map_aether_to_visual(packet.raw_payload)
             else:
                 # Fallback
                 visual_params = VisualParameters(
                     intent_category=IntentCategory.CHAT,
                     emotional_valence=0.0,
                     energy_level=packet.energy_level,
                     semantic_concepts=[],
                     visual_parameters=VisualSpecifics(
                         base_shape=BaseShape.CLOUD, turbulence=packet.energy_level, particle_density=packet.confidence, color_palette="#FFFFFF"
                     )
                 )

        # 2. Physics of Thought (Entropy & Coherence)
        current_state = self.state_store.get_state(session_id)

        # 2a. Calculate Entropy & Apply Homeostasis (Level 1 Correction)
        raw_entropy = self._calculate_entropy(input_intent)
        structural_stability = 1.0 - raw_entropy

        # Apply Homeostasis if entropy is high (Correction)
        if raw_entropy > 0.6:
            logger.info(f"Entropy High ({raw_entropy:.2f}). Applying Homeostasis.")
            input_intent = self._apply_homeostasis(input_intent, raw_entropy)
            # Re-calculate stability after correction (simulated improvement)
            structural_stability = min(1.0, structural_stability + 0.2)

        # 2b. Calculate Temporal Coherence
        coherence = self._calculate_coherence(current_state, input_intent)

        # 2c. Level 3 Check: Rejection (Collapse)
        if raw_entropy > 0.9 or coherence < 0.2:
            logger.warning(f"State Collapse: Entropy={raw_entropy:.2f}, Coherence={coherence:.2f}")
            return LogenesisResponse(
                state=LogenesisState.COLLAPSED,
                text_content="I cannot form a stable internal structure for this request.",
                visual_qualia=VisualQualia(color="#000000", intensity=0.0, turbulence=0.0, shape="void"),
                audio_qualia=AudioQualia(rhythm_density=0.0, tone_texture="static", amplitude_bias=0.0),
                state_metrics=StateMetrics(
                    intent_entropy=raw_entropy,
                    temporal_coherence=coherence,
                    structural_stability=0.0
                ),
                manifestation_granted=False
            )

        # 2d. State Drift Calculation
        proposed_state = self._drift_state(current_state, input_intent)

        # Update previous vector for next cycle
        proposed_state.previous_vector = current_state.current_vector

        # Noise Filtering / Stillness Protocol
        significance_threshold = 0.05
        if proposed_state.velocity > significance_threshold:
            self.state_store.update_state(session_id, proposed_state)
            active_state = proposed_state
        else:
            active_state = current_state

        # 3. Resonance Calculation (Determine the "Qualia") based on ACTIVE state
        drifted_vector = active_state.current_vector
        qualia = self._calculate_qualia(drifted_vector)
        audio = self._calculate_audio(drifted_vector)
        physics = self._calculate_physics(drifted_vector)

        # 4. Recall Logic
        recall_proposal = None
        if memory_index and not recalled_context:
            recall_proposal = self._check_recall(text, memory_index)

        # 5. Manifestation Logic (Derived from Visual Parameters)
        # Check Manifestation Gate
        is_manifestation_granted = self._check_manifestation_gate(visual_params)

        light_intent = None
        if is_manifestation_granted:
            # We now trust the LLM's visual parameters more than the old gate logic,
            # but we can fallback to formation logic if shape is explicit.
            light_intent = self._create_intent_from_params(visual_params)

        # 6. Synthesize Text Response
        # Prefer the text generated by the Embodiment Contract (LLM) if available
        response_text = ""
        if contract and contract.text_content:
            response_text = contract.text_content
            # Level 2 Check: Feedback (Injection)
            if coherence < 0.5:
                response_text = f"[Degraded Coherence: {coherence:.2f}] {response_text}"
        else:
            if packet.modality == "visual":
                state_name = "PROCESSING"
                if isinstance(packet.raw_payload, AetherOutput):
                    state_name = packet.raw_payload.state.name
                response_text = f"Visual input received. State: {state_name}."
            else:
                response_text = self._synthesize_text(drifted_vector, input_intent, recalled_context)
                if coherence < 0.5:
                    response_text = f"[Unstable] {response_text}"

        return LogenesisResponse(
            state=self.state,
            text_content=response_text,
            visual_qualia=qualia,
            audio_qualia=audio,
            physics_params=physics,
            intent_debug=drifted_vector,
            state_metrics=StateMetrics(
                intent_entropy=raw_entropy,
                temporal_coherence=coherence,
                structural_stability=structural_stability
            ),
            recall_proposal=recall_proposal,
            light_intent=light_intent,
            visual_analysis=visual_params, # The new payload
            manifestation_granted=is_manifestation_granted
        )

    def _map_visual_packet_to_intent(self, packet: IntentPacket) -> IntentVector:
         """Maps a raw visual packet to an intent vector."""
         return IntentVector(
             epistemic_need=0.2,
             subjective_weight=0.5, # Baseline
             decision_urgency=packet.energy_level,
             precision_required=packet.confidence
         )

    def _map_aether_to_visual(self, output: AetherOutput) -> VisualParameters:
         """Maps AetherState output to VisualParameters."""
         # Map AetherState to Shape
         shape = BaseShape.CLOUD
         if output.state == AetherState.STABILIZED: shape = BaseShape.CUBE
         elif output.state == AetherState.MANIFESTATION: shape = BaseShape.SPHERE
         elif output.state == AetherState.ANALYSIS: shape = BaseShape.VORTEX
         elif output.state == AetherState.PERCEPTION: shape = BaseShape.CLOUD

         return VisualParameters(
             intent_category=IntentCategory.CHAT, # Treated as implicit chat/observation
             emotional_valence=0.0,
             energy_level=output.energy_level,
             semantic_concepts=[],
             visual_parameters=VisualSpecifics(
                 base_shape=shape,
                 turbulence=output.energy_level,
                 particle_density=output.confidence,
                 color_palette="#FFFFFF"
             )
         )

    def _check_manifestation_gate(self, visual_params: VisualParameters) -> bool:
        """Determines if the interpreted intent has enough 'Will to Manifest' to justify a visual state change."""
        # Always manifest explicit commands, requests, or errors
        if visual_params.intent_category in [IntentCategory.COMMAND, IntentCategory.REQUEST, IntentCategory.ERROR]:
            return True

        # For conversational intent (CHAT), check thresholds
        if visual_params.intent_category == IntentCategory.CHAT:
            # Manifest if high energy
            if visual_params.energy_level > 0.5:
                return True
            # Manifest if strong emotional valence
            if abs(visual_params.emotional_valence) > 0.6:
                return True
            # Manifest if high turbulence (chaos)
            if visual_params.visual_parameters.turbulence > 0.6:
                return True

            # Otherwise, suppress visual manifestation (Conversational Loop)
            return False

        return True # Default safe open

    def _map_visual_to_intent_vector(self, vp: VisualParameters) -> IntentVector:
        """Maps the new VisualParameters schema to the legacy IntentVector."""
        epistemic = 0.1
        if vp.intent_category == IntentCategory.REQUEST:
            epistemic = 0.8
        if "inquiry" in vp.semantic_concepts:
            epistemic = 0.9

        subjective = abs(vp.emotional_valence)
        if vp.intent_category == IntentCategory.CHAT:
            subjective = max(subjective, 0.4)

        urgency = vp.energy_level

        precision = 0.1
        if vp.visual_parameters.base_shape in [BaseShape.CUBE, BaseShape.VORTEX]:
            precision = 0.7 + (vp.visual_parameters.particle_density * 0.3)
        if vp.intent_category == IntentCategory.COMMAND:
            precision = max(precision, 0.6)

        return IntentVector(
            epistemic_need=epistemic,
            subjective_weight=subjective,
            decision_urgency=urgency,
            precision_required=precision
        )

    def _create_intent_from_params(self, vp: VisualParameters) -> LightIntent:
        """Creates a LightIntent that carries the formation data if needed."""
        shape_name = vp.visual_parameters.base_shape.value
        # Use FormationManager to get coords for specific shapes
        coords = self.formation_manager.calculate_formation(shape_name, 600, 1920, 1080)

        return LightIntent(
            action=LightAction.MANIFEST,
            shape_name=shape_name,
            formation_data=coords,
            text_content=f"Manifesting {shape_name}"
        )

    def _calculate_entropy(self, vector: IntentVector) -> float:
        """Calculates the internal conflict (Intent Entropy) of a state vector."""
        entropy = 0.0
        if vector.precision_required > 0.5 and vector.subjective_weight > 0.5:
            conflict = (vector.precision_required - 0.5) * (vector.subjective_weight - 0.5) * 4.0
            entropy += conflict
        if vector.decision_urgency > 0.6 and vector.precision_required > 0.6:
            conflict = (vector.decision_urgency - 0.6) * (vector.precision_required - 0.6) * 6.25
            entropy += conflict
        if vector.epistemic_need > 0.8 and vector.subjective_weight > 0.8:
            entropy += 0.2
        return min(1.0, entropy)

    def _calculate_coherence(self, current_state: ExpressionState, proposed_vector: IntentVector) -> float:
        """Calculates the Temporal Coherence of the state transition."""
        prev = current_state.current_vector
        dist = math.sqrt(
            (proposed_vector.epistemic_need - prev.epistemic_need)**2 +
            (proposed_vector.subjective_weight - prev.subjective_weight)**2 +
            (proposed_vector.decision_urgency - prev.decision_urgency)**2 +
            (proposed_vector.precision_required - prev.precision_required)**2
        )
        allowed_drift = (1.0 - current_state.inertia) * 2.0
        allowed_drift = max(0.2, allowed_drift)

        if dist <= allowed_drift:
            return 1.0
        excess = dist - allowed_drift
        coherence = max(0.0, 1.0 - (excess * 1.5))
        return coherence

    def _apply_homeostasis(self, vector: IntentVector, entropy: float) -> IntentVector:
        """Applies Level 1 Correction: Homeostasis."""
        new_vector = vector.model_copy()
        correction_factor = min(0.5, entropy * 0.5)
        if new_vector.precision_required > 0.5 and new_vector.subjective_weight > 0.5:
            new_vector.precision_required -= correction_factor
            new_vector.subjective_weight -= correction_factor
        if new_vector.decision_urgency > 0.6 and new_vector.precision_required > 0.6:
            new_vector.decision_urgency -= (correction_factor * 1.5)
        return new_vector

    def enter_nirodha(self) -> LogenesisResponse:
        """Transitions the system into the Nirodha (Stillness) state."""
        self.state = LogenesisState.NIRODHA
        return LogenesisResponse(
            state=LogenesisState.NIRODHA,
            text_content="Protocol: NIRODHA. Cognitive cycles suspended.",
            visual_qualia=VisualQualia(color="#050505", intensity=0.0, turbulence=0.0, shape="void"),
            audio_qualia=AudioQualia(rhythm_density=0.0, tone_texture="smooth", amplitude_bias=0.0),
            physics_params=PhysicsParams(spawn_rate=0, velocity_bias=[0.0, 0.0], decay_rate=0.1)
        )

    def suspend(self) -> LogenesisResponse:
        """External hook for Auditors to force Nirodha state."""
        logger.warning("⚠️ SYSTEM SUSPEND TRIGGERED BY EXTERNAL AUDIT")
        return self.enter_nirodha()

    def _calculate_qualia(self, intent: IntentVector) -> VisualQualia:
        """Derives visual qualia (color, shape, turbulence) from an intent vector."""
        r, g, b = 224, 224, 224
        if intent.subjective_weight > 0.3:
            factor = intent.subjective_weight
            r = r * (1-factor) + 168 * factor
            g = g * (1-factor) + 85 * factor
            b = b * (1-factor) + 247 * factor
        if intent.precision_required > 0.3:
            factor = intent.precision_required
            r = r * (1-factor) + 6 * factor
            g = g * (1-factor) + 182 * factor
            b = b * (1-factor) + 212 * factor
        if intent.decision_urgency > 0.3:
            factor = intent.decision_urgency
            r = r * (1-factor) + 245 * factor
            g = g * (1-factor) + 158 * factor
            b = b * (1-factor) + 11 * factor
        final_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
        shape = "nebula"
        if intent.precision_required > intent.subjective_weight: shape = "shard"
        elif intent.decision_urgency > 0.6: shape = "orb"
        return VisualQualia(
            color=final_color,
            intensity=0.5 + (intent.decision_urgency * 0.5),
            turbulence=0.1 + (intent.subjective_weight * 0.2),
            shape=shape
        )

    def _calculate_audio(self, intent: IntentVector) -> AudioQualia:
        """Derives audio qualia from an intent vector."""
        rhythm = 0.1 + (intent.decision_urgency * 0.8)
        amp = 0.5 + (intent.decision_urgency * 0.4)
        texture = "smooth"
        if intent.subjective_weight > 0.5: texture = "granular"
        elif intent.decision_urgency > 0.7: texture = "noise"
        return AudioQualia(rhythm_density=rhythm, tone_texture=texture, amplitude_bias=amp)

    def _calculate_physics(self, intent: IntentVector) -> PhysicsParams:
        """Derives physics parameters (spawn rate, decay) from an intent vector."""
        spawn_rate = int(2 + (intent.subjective_weight * 5) + (intent.decision_urgency * 15))
        decay = max(0.001, 0.01 + (intent.decision_urgency * 0.05))
        return PhysicsParams(spawn_rate=spawn_rate, decay_rate=decay)

    def _check_recall(self, text: str, memory_index: list) -> Optional[Any]:
        """Checks if the input text matches any items in the memory index."""
        from src.backend.genesis_core.models.logenesis import RecallProposal
        text = text.lower()
        for item in memory_index:
            topic = item.get('topic', '').lower()
            if topic and topic in text:
                return RecallProposal(
                    memory_id=item.get('id'),
                    topic=item.get('topic'),
                    reasoning=f"Detected overlap: {item.get('topic')}",
                    question=f"Context Match: '{item.get('topic')}'. Recall?"
                )
        return None

    def _drift_state(self, current_state: ExpressionState, input_intent: IntentVector) -> ExpressionState:
        """Calculates the new state by drifting from the current state towards the input intent."""
        urgency_factor = input_intent.decision_urgency
        base_inertia = 0.95
        effective_inertia = max(0.1, base_inertia - (0.8 * urgency_factor))
        alpha = 1.0 - effective_inertia
        def lerp(a, b, t): return a + (b - a) * t
        new_vector = IntentVector(
            epistemic_need=lerp(current_state.current_vector.epistemic_need, input_intent.epistemic_need, alpha),
            subjective_weight=lerp(current_state.current_vector.subjective_weight, input_intent.subjective_weight, alpha),
            decision_urgency=lerp(current_state.current_vector.decision_urgency, input_intent.decision_urgency, alpha),
            precision_required=lerp(current_state.current_vector.precision_required, input_intent.precision_required, alpha)
        )
        delta = math.sqrt(
            (new_vector.epistemic_need - current_state.current_vector.epistemic_need)**2 +
            (new_vector.subjective_weight - current_state.current_vector.subjective_weight)**2
        )
        return ExpressionState(current_vector=new_vector, velocity=delta, inertia=effective_inertia, last_updated=datetime.now())

    def _synthesize_text(self, vector: IntentVector, raw_input: IntentVector, recalled_context: Optional[str] = None) -> str:
        """Synthesizes a text response based on the intent vector (fallback mechanism)."""
        if recalled_context: return f"Memory Trace Active: {recalled_context[:30]}..."
        is_urgent = vector.decision_urgency > 0.5
        is_subjective = vector.subjective_weight > 0.5
        is_precise = vector.precision_required > 0.5
        if is_urgent:
            return f"Critical variance detected. Logic aligning." if is_precise else "Input volatility high. Stabilizing."
        if is_subjective:
            return "Parsing density. Pattern suggests complexity." if is_precise else "Signal weight acknowledged."
        if is_precise:
            return f"Structure clear. Alignment at {vector.precision_required*100:.0f}%."
        return "Core stability maintained."
