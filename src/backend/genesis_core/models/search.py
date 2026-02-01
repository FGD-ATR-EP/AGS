from pydantic import BaseModel
from typing import Optional

class SearchIntent(BaseModel):
    intent: str = "SEARCH"
    query: str
    language: str = "en"
    depth: str = "summary" # "summary", "detailed", "fact"
    trust_level: str = "high"
    source: str = "unknown"
