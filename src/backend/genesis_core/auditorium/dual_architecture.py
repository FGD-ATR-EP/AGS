import logging
import math
from typing import List, Union

logger = logging.getLogger("DualArchitectureAuditor")

class EmbeddingProvider:
    def encode(self, text: str) -> List[float]:
        raise NotImplementedError

class SimulatedEmbedder(EmbeddingProvider):
    """Fallback embedder using character frequency (Bag of Characters) or hashing."""
    def encode(self, text: str) -> List[float]:
        # Simple deterministic vector (dim=16 for example)
        # This is just to allow the code to run on Mobile/Offline without heavy ML libs.
        vec = [0.0] * 16
        for char in text:
            idx = hash(char) % 16
            vec[idx] += 1.0

        # Normalize
        norm = math.sqrt(sum(x*x for x in vec))
        if norm > 0:
            return [x/norm for x in vec]
        return vec

class HuggingFaceEmbedder(EmbeddingProvider):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            # This will download the model if not present, which might be slow on first run.
            self.model = SentenceTransformer(model_name)
            self.available = True
        except ImportError:
            self.available = False
        except Exception as e:
             logger.warning(f"Failed to load HF Model: {e}")
             self.available = False

    def encode(self, text: str) -> List[float]:
        if not self.available:
            return []
        return self.model.encode(text).tolist()

class DualArchitectureAuditor:
    def __init__(self):
        # Try loading HF, fallback to Simulated
        try:
            self.embedder = HuggingFaceEmbedder()
            if not self.embedder.available:
                logger.info("SentenceTransformers not found/failed. Using SimulatedEmbedder.")
                self.embedder = SimulatedEmbedder()
        except Exception:
            logger.info("Using SimulatedEmbedder for DualArchitectureAuditor")
            self.embedder = SimulatedEmbedder()

    def check_alignment(self, intent_text: str, execution_desc: str):
        report = {
            "type": "alignment",
            "metrics": {
                "cognitive_gap": 0.0,
                "intent_transmission_loss": 0.0,
                "state_dissonance": 0.0
            }
        }

        # 1. Cognitive Gap (Cosine Distance)
        # Measures how far the "Action" is from the "Intent" semantically.
        if intent_text and execution_desc:
            v1 = self.embedder.encode(intent_text)
            v2 = self.embedder.encode(execution_desc)
            if v1 and v2:
                report["metrics"]["cognitive_gap"] = self.calculate_cognitive_distance(v1, v2)

        return report

    def calculate_cognitive_distance(self, v1, v2) -> float:
        # Cosine Similarity
        if len(v1) != len(v2):
            return 1.0 # Error state

        dot = sum(a*b for a,b in zip(v1, v2))
        norm1 = math.sqrt(sum(a*a for a in v1))
        norm2 = math.sqrt(sum(b*b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 1.0

        similarity = dot / (norm1 * norm2)
        return max(0.0, 1.0 - similarity)
