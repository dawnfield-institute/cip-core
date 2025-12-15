"""
Embeddings - Text to Vector

Uses sentence-transformers for embedding generation.
"""

from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class Embedder:
    """
    Text embedding generator.
    
    Uses sentence-transformers models.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
    ):
        """
        Initialize embedder.
        
        Args:
            model_name: Sentence transformer model name
            device: "cpu" or "cuda"
        """
        self.model_name = model_name
        self.device = device
        self._model = None
        
        logger.info(f"Embedder initialized: {model_name} on {device}")
    
    def _load_model(self):
        """Lazy-load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device=self.device)
                logger.info(f"Loaded embedding model: {self.model_name}")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
                raise
        return self._model
    
    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector as list of floats
        """
        model = self._load_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
        
        Returns:
            List of embedding vectors
        """
        model = self._load_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        model = self._load_model()
        return model.get_sentence_embedding_dimension()
