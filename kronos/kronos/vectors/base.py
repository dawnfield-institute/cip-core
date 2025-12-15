"""
Abstract Vector Backend Interface

All vector backends must implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class VectorBackendBase(ABC):
    """Abstract base class for vector backends."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    async def store(
        self,
        id: str,
        embedding: List[float],
        payload: Dict[str, Any],
    ) -> None:
        """Store an embedding with payload."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.0,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.
        
        Returns list of dicts with:
        - id: str
        - score: float
        - payload: dict
        """
        pass
    
    @abstractmethod
    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> None:
        """Delete a vector by ID."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy."""
        pass
