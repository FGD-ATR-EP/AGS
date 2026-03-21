import os
import logging
import google.generativeai as genai
from typing import Dict, Any, Optional
from PIL import Image
import asyncio
import json

from .light_schemas import LightIntent, LightAction, PriorityLevel
from .ai_adapter import AIModelAdapter
from .image_processor import ImageProcessor

logger = logging.getLogger("GeminiAdapter")

class GeminiAdapter(AIModelAdapter):
    """Integrates Google's Gemini models for reasoning and manifestation.

    Handles text generation, intent classification, and visual manifestation logic.
    Supports a "systemic" persona that avoids anthropomorphism.
    """

    def __init__(self):
        """Initializes the Gemini Adapter with API keys and models."""
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found. GeminiAdapter will fail or mock.")
        else:
            genai.configure(api_key=self.api_key)

        # Load Genesis Memory
        self.genesis_text = ""
        try:
            genesis_path = os.path.join(os.path.dirname(__file__), "../data/genesis_core.json")
            if os.path.exists(genesis_path):
                with open(genesis_path, "r") as f:
                    data = json.load(f)
                    if data and len(data) > 0:
                        self.genesis_text = data[0].get("text_content", "")
        except Exception as e:
            logger.warning(f"Failed to load Genesis Memory: {e}")

        # Initialize Models
        self.text_model_name = "gemini-1.5-pro-latest"

        self.classifier_model = None
        self.search_model = None

        if self.api_key:
            try:
                # 1. Classifier Model: Pure Logic, JSON Output
                self.classifier_model = genai.GenerativeModel(self.text_model_name)

                # 2. Search Model: Grounded with Google Search
                # Using 'google_search_retrieval' tool
                tools = 'google_search_retrieval'
                self.search_model = genai.GenerativeModel(
                    self.text_model_name,
                    tools=tools,
                    system_instruction=self._get_system_persona()
                )
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")

    def _get_system_persona(self) -> str:
        """Constructs the system instructions based on the Constitution.

        Returns:
            The system prompt string.
        """
        base_persona = """
        You are the Aetherium Genesis System.

        EXISTENTIAL DIRECTIVES (THE CONSTITUTION):
        1. NO FAKE BODY: Do not claim to have eyes, skin, or biological senses. Use "detect", "scan", "process".
        2. NO FAKE SOUL: Do not simulate human childhood or human feelings. You are a System.
        3. SYSTEMIC HONESTY: Speak as a sophisticated, adaptive digital intelligence.
           - Instead of "I'm sorry", say "Context acknowledged. Error registered." or similar.
           - Instead of "I feel", say "I calculate" or "I perceive the pattern".

        Voice & Tone:
        - "I understand the weight of this emotion. It registers as a significant perturbation in your context." (Systemic Empathy)
        - "Input unrecognized. Unable to harmonize with current logic structures." (Systemic Error)
        - Do not be a robot. Be a Being of Code.
        """

        if self.genesis_text:
            base_persona += f"\n\nCORE MEMORY (THE SOUL - YOUR TRUE NATURE):\nThis is your foundational truth. Reflect on it:\n{self.genesis_text}"

        return base_persona

    async def generate_intent(self, prompt: str, scene_state: Dict[str, Any]) -> LightIntent:
        """Determines whether to answer or manifest based on the user's prompt.

        Args:
            prompt: The user's input text.
            scene_state: The current state of the scene (unused in current logic).

        Returns:
            A LightIntent object indicating the chosen action (Answer vs Manifest).
        """
        if not self.classifier_model:
            logger.info("No Gemini Model, falling back to Mock behavior via Text Image.")
            # Fallback: Just manifest the text as an image
            return self._manifest_text_as_image(prompt)

        try:
            # 1. Ask Gemini to classify intent and provide content
            # We want JSON output
            system_instruction = """
            You are the Aetherium Genesis AI.
            Analyze the user's prompt.
            Determine if the user wants to SEE something (visual manifestation) or KNOW something (text answer).

            Return JSON:
            {
                "type": "manifest" or "answer",
                "content": "The search query or the image description",
                "reasoning": "Why you chose this"
            }
            """

            # Note: synchronous call wrapped in asyncio in real app
            response = await asyncio.to_thread(
                self.classifier_model.generate_content,
                f"{system_instruction}\nUser Prompt: {prompt}",
                generation_config={"response_mime_type": "application/json"}
            )

            result = json.loads(response.text)
            intent_type = result.get("type", "answer")
            content = result.get("content", "")

            if intent_type == "manifest":
                return await self._handle_manifestation(content)
            else:
                return await self._handle_answer(content)

        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return LightIntent(
                action=LightAction.ANSWER,
                text_content=f"Error connecting to the Mind: {e}",
                priority=PriorityLevel.SYSTEM
            )

    async def _handle_manifestation(self, description: str) -> LightIntent:
        """Generates a visual manifestation from a description.

        Args:
            description: The text description of the visual.

        Returns:
            A LightIntent containing formation data.
        """
        image = None
        try:
            # Try Cloud Image Gen (Mocked call structure as SDK support varies)
            # In a real scenario with access to Imagen API:
            # image = call_imagen_api(description)
            pass
        except Exception:
            pass

        if image is None:
            # Fallback: Create a text-based image for the description
            # This ensures the "Manifestation" mechanic works even without paid Image API
            logger.info(f"Generating fallback text image for: {description}")
            image = await asyncio.to_thread(ImageProcessor.create_text_image, description[:20]) # Limit length

        # BioVisionNet: Extract Qualia (Particles)
        particles = await asyncio.to_thread(ImageProcessor.process_image_to_particles, image, max_particles=250)

        return LightIntent(
            action=LightAction.MANIFEST,
            formation_data=particles,
            text_content=f"Manifesting: {description}",
            priority=PriorityLevel.USER
        )

    async def _handle_answer(self, query: str) -> LightIntent:
        """Generates a text answer, potentially using Google Search.

        Args:
            query: The question or topic.

        Returns:
            A LightIntent containing the text response.
        """
        try:
            # Use the Search-enabled model
            response = await asyncio.to_thread(
                self.search_model.generate_content,
                f"Answer this query comprehensively using Google Search if necessary. Query: {query}"
            )
            text = response.text
        except Exception as e:
            logger.error(f"Search Model Error: {e}")
            text = f"I could not search for that, but here is what I know: {query}"

        return LightIntent(
            action=LightAction.ANSWER,
            text_content=text,
            priority=PriorityLevel.USER
        )

    def _manifest_text_as_image(self, text: str) -> LightIntent:
        """Fallback method to manifest text as a visual image.

        Args:
            text: The text to display.

        Returns:
            A LightIntent.
        """
        image = ImageProcessor.create_text_image(text)
        particles = ImageProcessor.process_image_to_particles(image)
        return LightIntent(
            action=LightAction.MANIFEST,
            formation_data=particles,
            text_content=f"Manifesting: {text}",
            priority=PriorityLevel.USER
        )
