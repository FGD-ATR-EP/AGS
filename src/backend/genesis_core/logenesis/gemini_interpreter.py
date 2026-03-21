import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
import google.generativeai as genai

from .interpreter import IntentInterpreter
from src.backend.genesis_core.models.visual import EmbodimentContract
from .verifier import VisualVerifier

logger = logging.getLogger("GeminiInterpreter")

class GeminiIntentInterpreter(IntentInterpreter):
    """Implementation of IntentInterpreter using Google's Gemini Pro.

    Acts as the 'Visual Translator' mapping natural language to the
    Aetherium Genesis EmbodimentContract schema via LLM prompts.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initializes the Gemini model.

        Args:
            api_key: Google Gemini API Key. Defaults to GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model = None

        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found. GeminiInterpreter will not function.")
        else:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=self._get_system_prompt()
                )
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

    def _get_system_prompt(self) -> str:
        """Returns the system prompt defining the cognitive laws and JSON schema.

        Returns:
            The system instruction string.
        """
        return """
        You are the 'Cognitive Core' of the Aetherium Genesis system.
        Your task is to generate an 'Embodiment Contract' (JSON) that defines your internal state, intent, and verbal response.

        THE PHILOSOPHY (The 3 Laws):
        1. Conservation of Energy: Complex tasks require high 'effort'.
        2. Visibility of Entropy: Uncertainty must be confessed via 'uncertainty' parameter.
        3. Topology of Intent: The shape of your thought depends on the category (Analytic=Structured, Creative=Organic).

        OUTPUT JSON SCHEMA (EmbodimentContract):
        Return ONLY valid JSON matching this structure:
        {
          "temporal_state": {
            "phase": "MANIFESTING",  // Always 'MANIFESTING' for the final response.
            "stability": 0.8,        // 0.0 (Volatile/Changing) -> 1.0 (Stable/Locked)
            "duration_ms": 0
          },
          "cognitive": {
            "effort": 0.5,           // 0.0 (Reflex/Easy) -> 1.0 (Deep Reasoning/Hard)
            "uncertainty": 0.1,      // 0.0 (Confident) -> 1.0 (Confused/Guessing)
            "latency_factor": 0.0
          },
          "intent": {
            "category": "CHIT_CHAT", // Options: CHIT_CHAT, ANALYTIC, CREATIVE, SYSTEM_OPS
            "purity": 1.0            // 0.0 (Mixed) -> 1.0 (Pure Intent)
          },
          "text_content": "Write your verbal response to the user here."
        }

        INTENT CATEGORIES:
        - ANALYTIC: For logic, math, code, definitions, specific questions. (Maps to Cubic forms)
        - CREATIVE: For stories, poems, ideas, abstract thoughts. (Maps to Nebula forms)
        - SYSTEM_OPS: For system commands, errors, technical acknowledgments. (Maps to Grid forms)
        - CHIT_CHAT: For greetings, small talk, empathy. (Maps to Sphere forms)
        """

    async def interpret(self, text: str, context: Optional[Dict[str, Any]] = None) -> EmbodimentContract:
        """Generates an EmbodimentContract from user text using Gemini.

        Constructs a prompt with context, invokes the LLM, parses the JSON response,
        and verifies it against the schema.

        Args:
            text: The user input text.
            context: Optional conversational context.

        Returns:
            A verified EmbodimentContract.

        Raises:
            RuntimeError: If the model is not initialized.
            Exception: If generation or parsing fails.
        """
        if not self.model:
            raise RuntimeError("Gemini model not initialized")

        try:
            # Construct the prompt with context
            prompt = f"User Input: {text}\n"
            if context:
                prompt += f"Context: {json.dumps(context)}\n"

            # Call Gemini (async wrapper)
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            raw_json = response.text
            try:
                data = json.loads(raw_json)
            except json.JSONDecodeError:
                # Sometimes models wrap in markdown ```json ... ``` despite mime_type
                if "```json" in raw_json:
                    raw_json = raw_json.split("```json")[1].split("```")[0].strip()
                    data = json.loads(raw_json)
                else:
                    raise

            # Verify and Repair
            return VisualVerifier.verify_contract(data)

        except Exception as e:
            logger.error(f"Gemini Interpretation failed: {e}")
            raise e
