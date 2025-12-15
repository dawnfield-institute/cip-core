"""
Kronos Storage - Unified Interface

Combines graph and vector backends for repository knowledge graphs.
"""

from __future__ import annotations

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from .types import RepoNode, RepoEdge, NodeType, RelationType, QueryResult

logger = logging.getLogger(__name__)


class KronosStorage:
    """
    Main interface for Kronos repository knowledge graphs.
    
    Combines:
    - Graph DB (Neo4j or SQLite) for relationships
    - Vector DB (Qdrant or ChromaDB) for semantic search
    - Embeddings for content vectorization
    """
    
    def __init__(
        self,
        graph_backend: str = "sqlite",
        vector_backend: str = "chromadb",
        graph_uri: str = "kronos.db",
        vector_uri: str = "./kronos_vectors",
        embedding_model: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
    ):
        """
        Initialize Kronos storage.
        
        Args:
            graph_backend: "sqlite" or "neo4j"
            vector_backend: "chromadb" or "qdrant"
            graph_uri: Connection URI for graph DB
            vector_uri: Connection URI for vector DB
            embedding_model: Sentence transformer model
            device: "cpu" or "cuda"
        """
        self.graph_backend_type = graph_backend
        self.vector_backend_type = vector_backend
        self.graph_uri = graph_uri
        self.vector_uri = vector_uri
        self.embedding_model_name = embedding_model
        self.device = device
        
        # Backends (lazy-loaded)
        self._graph = None
        self._vectors = None
        self._embedder = None
        
        logger.info(
            f"Kronos initialized: graph={graph_backend}, "
            f"vectors={vector_backend}, device={device}"
        )
    
    async def connect(self):
        """Establish connections to backends."""
        # Initialize graph backend
        if self.graph_backend_type == "sqlite":
            from .graph.sqlite import SQLiteGraphBackend
            self._graph = SQLiteGraphBackend(self.graph_uri)
        elif self.graph_backend_type == "neo4j":
            from .graph.neo4j import Neo4jGraphBackend
            self._graph = Neo4jGraphBackend(self.graph_uri)
        else:
            raise ValueError(f"Unknown graph backend: {self.graph_backend_type}")
        
        await self._graph.connect()
        
        # Initialize vector backend
        if self.vector_backend_type == "chromadb":
            from .vectors.chromadb import ChromaDBBackend
            self._vectors = ChromaDBBackend(self.vector_uri)
        elif self.vector_backend_type == "qdrant":
            from .vectors.qdrant import QdrantBackend
            self._vectors = QdrantBackend(self.vector_uri)
        else:
            raise ValueError(f"Unknown vector backend: {self.vector_backend_type}")
        
        await self._vectors.connect()
        
        # Initialize embedder
        from .embeddings import Embedder
        self._embedder = Embedder(self.embedding_model_name, self.device)
        
        logger.info("Kronos backends connected")
    
    async def close(self):
        """Close backend connections."""
        if self._graph:
            await self._graph.close()
        if self._vectors:
            await self._vectors.close()
        logger.info("Kronos backends closed")
    
    async def store_node(
        self,
        content: str,
        node_type: NodeType,
        path: str,
        metadata: Optional[Dict[str, Any]] = None,
        node_id: Optional[str] = None,
    ) -> str:
        """
        Store a node in the knowledge graph.
        
        Args:
            content: Text content
            node_type: Type of node
            path: Repository path
            metadata: Additional metadata
            node_id: Optional ID (auto-generated if not provided)
        
        Returns:
            Node ID
        """
        if node_id is None:
            node_id = str(uuid.uuid4())
        
        # Generate embedding
        embedding = await self._embedder.embed(content)
        
        # Build node
        node = RepoNode(
            id=node_id,
            type=node_type,
            path=path,
            content=content,
            embedding=embedding,
            name=metadata.get("name") if metadata else None,
            language=metadata.get("language") if metadata else None,
            line_start=metadata.get("line_start") if metadata else None,
            line_end=metadata.get("line_end") if metadata else None,
            description=metadata.get("description") if metadata else None,
            semantic_scope=metadata.get("semantic_scope") if metadata else None,
            proficiency_level=metadata.get("proficiency_level") if metadata else None,
            metadata=metadata or {},
        )
        
        # Store in both backends
        await self._graph.create_node(node)
        await self._vectors.store(node_id, embedding, node.to_dict())
        
        logger.debug(f"Stored node: {node_id} ({node_type.value})")
        return node_id
    
    async def create_edge(
        self,
        from_id: str,
        to_id: str,
        relation: RelationType,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create an edge between nodes.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            relation: Relationship type
            weight: Edge weight
            metadata: Additional metadata
        
        Returns:
            Edge ID
        """
        edge_id = str(uuid.uuid4())
        
        edge = RepoEdge(
            id=edge_id,
            from_id=from_id,
            to_id=to_id,
            relation=relation,
            weight=weight,
            metadata=metadata or {},
        )
        
        await self._graph.create_edge(edge)
        
        logger.debug(f"Created edge: {from_id} -{relation.value}-> {to_id}")
        return edge_id
    
    async def query(
        self,
        query_text: str,
        limit: int = 10,
        node_types: Optional[List[NodeType]] = None,
        expand_graph: bool = True,
        threshold: float = 0.5,
    ) -> List[QueryResult]:
        """
        Semantic search across the knowledge graph.
        
        Args:
            query_text: Natural language query
            limit: Max results
            node_types: Filter by node types
            expand_graph: Whether to expand via relationships
            threshold: Minimum similarity threshold
        
        Returns:
            Ranked query results
        """
        # Generate query embedding
        query_embedding = await self._embedder.embed(query_text)
        
        # Vector search
        vector_results = await self._vectors.search(
            query_embedding,
            limit=limit * 2 if expand_graph else limit,
            threshold=threshold,
        )
        
        # Build results
        results = []
        for vr in vector_results:
            node = RepoNode.from_dict(vr["payload"])
            
            # Filter by node type if specified
            if node_types and node.type not in node_types:
                continue
            
            results.append(QueryResult(
                node=node,
                score=vr["score"],
            ))
        
        # Expand through graph if requested
        if expand_graph and results:
            results = await self._expand_results(results, limit)
        
        return results[:limit]
    
    async def _expand_results(
        self,
        results: List[QueryResult],
        limit: int,
    ) -> List[QueryResult]:
        """Expand results through graph relationships."""
        # Get neighbors of top results
        seen_ids = {r.node.id for r in results}
        expanded = list(results)
        
        for result in results[:5]:  # Expand top 5
            neighbors = await self._graph.get_neighbors(
                result.node.id,
                max_depth=1,
            )
            
            for neighbor in neighbors:
                if neighbor.id not in seen_ids:
                    seen_ids.add(neighbor.id)
                    expanded.append(QueryResult(
                        node=neighbor,
                        score=result.score * 0.8,  # Decay
                        path_strength=result.score * 0.8,
                        expanded_via_graph=True,
                    ))
        
        # Sort by strength
        expanded.sort(key=lambda r: r.strength, reverse=True)
        return expanded
    
    async def get_node(self, node_id: str) -> Optional[RepoNode]:
        """Get a node by ID."""
        return await self._graph.get_node(node_id)
    
    async def get_edges(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        direction: str = "both",
    ) -> List[RepoEdge]:
        """Get edges for a node."""
        return await self._graph.get_edges(node_id, relation_types, direction)
    
    async def trace_evolution(
        self,
        node_id: str,
        direction: str = "backward",
        max_depth: int = 10,
    ) -> List[RepoNode]:
        """
        Trace temporal evolution via EVOLVES_FROM edges.
        
        Args:
            node_id: Starting node
            direction: "forward", "backward", or "both"
            max_depth: Maximum path length
        
        Returns:
            List of nodes in evolution chain
        """
        return await self._graph.trace_path(
            node_id,
            relation_types=[RelationType.EVOLVES_FROM, RelationType.EVOLVES_TO],
            direction=direction,
            max_depth=max_depth,
        )
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all backends."""
        return {
            "graph": await self._graph.health_check() if self._graph else False,
            "vectors": await self._vectors.health_check() if self._vectors else False,
        }
