from ..models.light import LightIntent, LightAction, TemporalType
from ..models.search import SearchIntent
import re
from typing import Dict, Any, Union

class LightweightAI:
    """Lightweight AI Core.

    A rule-based resolver for immediate feedback and baseline testing.
    Handles simple touch and voice commands without invoking external LLMs.
    """

    def resolve_intent(self, input_data: Dict[str, Any]) -> Union[LightIntent, SearchIntent]:
        """Resolves raw input data into a structured intent.

        Args:
            input_data: A dictionary containing input type and parameters (e.g., touch region, voice text).

        Returns:
            A LightIntent or SearchIntent based on rule matching.
        """
        input_type = input_data.get("type")

        if input_type == "touch":
            region = input_data.get("region")
            # Ensure region is a tuple if it exists
            if region and isinstance(region, list):
                region = tuple(region)

            return LightIntent(
                action=LightAction.SPAWN,
                region=region,
                intensity=input_data.get("pressure", 0.5),
                temporal=TemporalType.CONTINUOUS
            )

        if input_type == "voice":
            text = input_data.get("text", "").lower()

            # Check for Search Intent
            search_match = re.search(r"(search for|search|find|ค้นหา)\s+(.*)", text)
            if search_match:
                query = search_match.group(2).strip()
                return SearchIntent(query=query, source="voice")

            if re.search(r"move|ย้าย", text):
                return LightIntent(action=LightAction.MOVE)
            if re.search(r"erase|ลบ", text):
                return LightIntent(action=LightAction.ERASE)

        # Default behavior
        return LightIntent(action=LightAction.EMPHASIZE)
