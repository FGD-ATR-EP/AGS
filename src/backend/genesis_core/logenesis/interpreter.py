from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.backend.genesis_core.models.visual import EmbodimentContract

class IntentInterpreter(ABC):
    """Abstract Base Class for interpreting natural language into EmbodimentContract.

    Follows the 'Visual Translator' role described in Aetherium Genesis, responsible for
    converting raw user input into structured cognitive and visual intents.
    """

    @abstractmethod
    async def interpret(self, text: str, context: Optional[Dict[str, Any]] = None) -> EmbodimentContract:
        """Translates the user's text (and optional context) into an EmbodimentContract object.

        Args:
            text: The raw input text from the user.
            context: Optional dictionary containing conversational or system context.

        Returns:
            An EmbodimentContract describing the system's intent, cognitive state, and response.
        """
        pass
