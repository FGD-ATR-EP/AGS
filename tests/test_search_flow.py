import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.backend.genesis_core.logenesis.lightweight_ai import LightweightAI
from backend.core.search_schemas import SearchIntent
from backend.core.google_search_provider import GoogleSearchProvider
from backend.core.lcl import LightControlLogic
from backend.core.light_schemas import LightIntent, LightAction
from src.backend.genesis_core.models.search import SearchIntent
from src.backend.departments.marketing.google_search_provider import GoogleSearchProvider
from src.backend.departments.presentation.lcl import LightControlLogic
from src.backend.genesis_core.models.light import LightIntent, LightAction

class TestSearchFlow(unittest.TestCase):
    def test_intent_extraction(self):
        ai = LightweightAI()

        # Test Search
        input_data = {"type": "voice", "text": "search for quantum computing"}
        intent = ai.resolve_intent(input_data)
        self.assertIsInstance(intent, SearchIntent)
        self.assertEqual(intent.query, "quantum computing")

        # Test Other
        input_data = {"type": "voice", "text": "move this"}
        intent = ai.resolve_intent(input_data)
        self.assertIsInstance(intent, LightIntent)
        self.assertEqual(intent.action, LightAction.MOVE)

    @patch('requests.get')
    def test_provider_and_synthesis(self, mock_get):
        # Setup Mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "items": [
                {"title": "Quantum", "snippet": "A summary of quantum mechanics."}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Initialize
        provider = GoogleSearchProvider(api_key="TEST", cse_id="TEST")
        lcl = LightControlLogic()

        # Execute Search
        query = "quantum"
        results = provider.search(query)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Quantum")

        # Synthesize (simulate server logic)
        summary = f"{results[0]['title']}: {results[0]['snippet']}"
        light_intent = LightIntent(
            action=LightAction.EMPHASIZE,
            target="GLOBAL",
            intensity=0.8,
            color_hint="white",
            source="search_provider"
        )

        instruction = lcl.process(light_intent)
        self.assertIsNotNone(instruction)

        # Manually attach text (as server does)
        instruction.text_content = summary

        self.assertEqual(instruction.text_content, "Quantum: A summary of quantum mechanics.")
        self.assertEqual(instruction.color_profile, "white")

if __name__ == '__main__':
    unittest.main()
