"""
Abstract Graph Backend Interface

All graph backends must implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..types import RepoNode, RepoEdge, RelationType


class GraphBackendBase(ABC):
    """Abstract base class for graph backends."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    async def create_node(self, node: RepoNode) -> None:
        """Create a node in the graph."""
        pass
    
    @abstractmethod
    async def get_node(self, node_id: str) -> Optional[RepoNode]:
        """Get a node by ID."""
        pass
    
    @abstractmethod
    async def update_node(self, node: RepoNode) -> None:
        """Update an existing node."""
        pass
    
    @abstractmethod
    async def delete_node(self, node_id: str) -> None:
        """Delete a node and its edges."""
        pass
    
    @abstractmethod
    async def create_edge(self, edge: RepoEdge) -> None:
        """Create an edge between nodes."""
        pass
    
    @abstractmethod
    async def get_edges(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        direction: str = "both",
    ) -> List[RepoEdge]:
        """Get edges for a node."""
        pass
    
    @abstractmethod
    async def delete_edge(self, edge_id: str) -> None:
        """Delete an edge."""
        pass
    
    @abstractmethod
    async def get_neighbors(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 1,
    ) -> List[RepoNode]:
        """Get neighboring nodes."""
        pass
    
    @abstractmethod
    async def trace_path(
        self,
        node_id: str,
        relation_types: List[RelationType],
        direction: str = "both",
        max_depth: int = 10,
    ) -> List[RepoNode]:
        """Trace a path through specific relationship types."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy."""
        pass
