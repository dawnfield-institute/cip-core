"""
ChromaDB Vector Backend

Simple embedded vector database - no Docker required.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .base import VectorBackendBase

logger = logging.getLogger(__name__)


class ChromaDBBackend(VectorBackendBase):
    """
    ChromaDB-based vector backend.
    
    Embedded database, no server required.
    Good for development and small/medium repositories.
    """
    
    def __init__(
        self,
        persist_directory: str = "./kronos_vectors",
        collection_name: str = "kronos",
    ):
        """
        Initialize ChromaDB backend.
        
        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        logger.info(f"ChromaDB backend: {persist_directory}")
    
    async def connect(self) -> None:
        """Initialize ChromaDB client."""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Create persist directory
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )
            
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            logger.info(f"ChromaDB collection '{self.collection_name}' ready")
            
        except ImportError:
            raise ImportError(
                "chromadb package not installed. "
                "Install with: pip install chromadb"
            )
    
    async def close(self) -> None:
        """Close ChromaDB (persists automatically)."""
        self.collection = None
        self.client = None
    
    async def store(
        self,
        id: str,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Store an embedding."""
        # ChromaDB stores metadata as flat dict with string values
        # Serialize complex values
        import json
        
        metadata = {}
        documents = []
        
        for key, value in payload.items():
            if key == "content":
                documents.append(value)
            elif isinstance(value, (str, int, float, bool)):
                metadata[key] = value
            elif value is not None:
                metadata[key] = json.dumps(value)
        
        self.collection.upsert(
            ids=[id],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else None,
            documents=documents if documents else None,
        )
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.0,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where=filter,
            include=["embeddings", "metadatas", "documents", "distances"],
        )
        
        # Convert to standard format
        output = []
        
        if results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            distances = results["distances"][0] if results.get("distances") else [0] * len(ids)
            metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
            documents = results["documents"][0] if results.get("documents") else [""] * len(ids)
            
            for i, id in enumerate(ids):
                # ChromaDB returns distance, convert to similarity
                # For cosine distance: similarity = 1 - distance
                distance = distances[i]
                score = 1 - distance
                
                if score < threshold:
                    continue
                
                payload = dict(metadatas[i]) if metadatas[i] else {}
                if documents[i]:
                    payload["content"] = documents[i]
                
                output.append({
                    "id": id,
                    "score": score,
                    "payload": payload,
                })
        
        return output
    
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        results = self.collection.get(
            ids=[id],
            include=["embeddings", "metadatas", "documents"],
        )
        
        if not results["ids"]:
            return None
        
        payload = dict(results["metadatas"][0]) if results["metadatas"] else {}
        if results["documents"] and results["documents"][0]:
            payload["content"] = results["documents"][0]
        
        return {
            "id": id,
            "embedding": results["embeddings"][0] if results["embeddings"] else None,
            "payload": payload,
        }
    
    async def delete(self, id: str) -> None:
        """Delete a vector."""
        self.collection.delete(ids=[id])
    
    async def health_check(self) -> bool:
        """Check ChromaDB health."""
        try:
            self.collection.count()
            return True
        except Exception:
            return False
