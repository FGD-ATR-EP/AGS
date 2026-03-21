import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from .interpreter import IntentInterpreter
from src.backend.genesis_core.models.visual import (
    EmbodimentContract, TemporalState, CognitiveMetadata, IntentData,
    TemporalPhase, ContractIntentCategory
)

class SimulatedIntentInterpreter(IntentInterpreter):
    """A deterministic interpreter for testing and fallback scenarios.

    Maps specific keywords to predefined EmbodimentContracts, allowing for consistent
    behavior verification without reliance on external LLM APIs.
    """

    async def interpret(self, text: str, context: Optional[Dict[str, Any]] = None) -> EmbodimentContract:
        """Interprets text using keyword matching to generate a simulated contract.

        Args:
            text: The user input text.
            context: Optional context (unused in simulation).

        Returns:
            A deterministic EmbodimentContract based on input keywords.
        """
        text = text.lower()

        # Defaults
        phase = TemporalPhase.MANIFESTING
        stability = 1.0

        effort = 0.3
        uncertainty = 0.1

        category = ContractIntentCategory.CHIT_CHAT
        purity = 1.0

        text_response = "I hear you."

        # 1. Detect Category
        if any(w in text for w in ["search", "find", "analyze", "check", "what", "how", "solve"]):
            category = ContractIntentCategory.ANALYTIC
            effort = 0.8
            text_response = "Analyzing data structure."
        elif any(w in text for w in ["stop", "start", "reset", "clear", "system", "status"]):
            category = ContractIntentCategory.SYSTEM_OPS
            effort = 0.2
            text_response = "System operations engaged."
        elif any(w in text for w in ["story", "imagine", "create", "poem", "idea"]):
            category = ContractIntentCategory.CREATIVE
            effort = 0.6
            uncertainty = 0.3 # Creative chaos
            text_response = "Imagining a new possibility."

        # 2. Detect Nuance
        if "hard" in text or "complex" in text:
            effort = 1.0
        if "maybe" in text or "unsure" in text:
            uncertainty = 0.8

        return EmbodimentContract(
            temporal_state=TemporalState(phase=phase, stability=stability, duration_ms=0),
            cognitive=CognitiveMetadata(effort=effort, uncertainty=uncertainty),
            intent=IntentData(category=category, purity=purity),
            text_content=text_response
        )
