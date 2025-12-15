"""
Qdrant Vector Backend

Production-grade vector database.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional

from .base import VectorBackendBase

logger = logging.getLogger(__name__)


class QdrantBackend(VectorBackendBase):
    """
    Qdrant-based vector backend.
    
    High-performance vector database for production use.
    Requires Qdrant server (Docker recommended).
    """
    
    def __init__(
        self,
        uri: str = "localhost:6333",
        collection_name: str = "kronos",
        vector_size: int = 384,  # all-MiniLM-L6-v2 dimension
    ):
        """
        Initialize Qdrant backend.
        
        Args:
            uri: Qdrant server URI (host:port or URL)
            collection_name: Name of the collection
            vector_size: Embedding dimension
        """
        self.uri = uri
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = None
        
        logger.info(f"Qdrant backend: {uri}")
    
    async def connect(self) -> None:
        """Connect to Qdrant server."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            # Parse URI
            if ":" in self.uri and not self.uri.startswith("http"):
                host, port = self.uri.split(":")
                self.client = QdrantClient(host=host, port=int(port))
            else:
                self.client = QdrantClient(url=self.uri)
            
            # Ensure collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            
            logger.info("Qdrant connection established")
            
        except ImportError:
            raise ImportError(
                "qdrant-client package not installed. "
                "Install with: pip install qdrant-client"
            )
    
    async def close(self) -> None:
        """Close Qdrant connection."""
        self.client = None
    
    async def store(
        self,
        id: str,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Store an embedding."""
        from qdrant_client.models import PointStruct
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.0,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Build filter if provided
        qdrant_filter = None
        if filter:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter.items()
            ]
            qdrant_filter = Filter(must=conditions)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
            query_filter=qdrant_filter,
        )
        
        return [
            {
                "id": str(r.id),
                "score": r.score,
                "payload": r.payload or {},
            }
            for r in results
        ]
    
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        results = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[id],
            with_vectors=True,
            with_payload=True,
        )
        
        if not results:
            return None
        
        point = results[0]
        return {
            "id": str(point.id),
            "embedding": point.vector,
            "payload": point.payload or {},
        }
    
    async def delete(self, id: str) -> None:
        """Delete a vector."""
        from qdrant_client.models import PointIdsList
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=PointIdsList(points=[id]),
        )
    
    async def health_check(self) -> bool:
        """Check Qdrant health."""
        try:
            self.client.get_collection(self.collection_name)
            return True
        except Exception:
            return False
