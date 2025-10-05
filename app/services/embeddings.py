"""Text embeddings for semantic search"""

from typing import List
import logging
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Generate embeddings using Vertex AI"""
    
    def __init__(self):
        aiplatform.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.VERTEX_AI_LOCATION
        )
        self.model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        try:
            embeddings = self.model.get_embeddings([text])
            return embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = self.model.get_embeddings(texts)
            return [emb.values for emb in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            return []


embedding_service = EmbeddingService()

