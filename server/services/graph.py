"""Knowledge Graph Service - Kronos-powered repository understanding."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class QueryResult:
    """Result from a graph query."""
    id: str
    type: str
    path: str
    content: str
    score: float
    metadata: dict = None


class KnowledgeGraphService:
    """
    Service for querying and managing the repository knowledge graph.
    
    Powered by Kronos (adapted from GRIMM).
    """
    
    def __init__(self, storage):
        """Initialize with Kronos storage backend."""
        self.storage = storage  # KronosStorage instance
        
    async def query(
        self,
        query: str,
        repo: Optional[str] = None,
        limit: int = 10,
        expand_graph: bool = False
    ) -> list[QueryResult]:
        """
        Semantic search across the knowledge graph.
        """
        from kronos.types import NodeType
        
        # Use Kronos storage query
        results = await self.storage.query(query_text=query, limit=limit, expand_graph=expand_graph)
        
        return results
    
    async def get_node(self, node_id: str) -> Optional[dict]:
        """Get a specific node by ID."""
        node = await self.storage.get_node(node_id)
        # Handle both dict and object returns
        if node and hasattr(node, 'to_dict'):
            return node.to_dict()
        return node
    
    async def trace_concept(
        self,
        concept: str,
        depth: int = 5
    ) -> list[dict]:
        """
        Trace temporal evolution of a concept.
        
        Follows EVOLVES_FROM edges backwards in time.
        """
        # First find nodes matching the concept
        results = await self.storage.query(concept, limit=5)
        
        if not results:
            return []
        
        # Get first result
        first_result = results[0]
        if isinstance(first_result, dict):
            node_id = first_result.get('id')
        else:
            node_id = first_result.node.id if hasattr(first_result, 'node') else first_result.id
        
        # Trace evolution from top result
        evolution_chain = await self.storage.trace_evolution(
            node_id,
            direction="backward",
            max_depth=depth,
        )
        
        # Handle both dict and object results
        result_list = []
        for item in evolution_chain:
            if isinstance(item, dict):
                result_list.append(item)
            elif hasattr(item, 'to_dict'):
                result_list.append(item.to_dict())
            else:
                result_list.append(item)
        
        return result_list
    
    async def find_related(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        limit: int = 10
    ) -> list[dict]:
        """Find nodes related to a given node."""
        from kronos.types import RelationType
        
        relation_types = None
        if relationship_type:
            relation_types = [RelationType(relationship_type)]
        
        edges = await self.storage.get_edges(node_id, relation_types)
        
        # Get target nodes
        related = []
        for edge in edges[:limit]:
            # Handle both dict and object edges
            if isinstance(edge, dict):
                target_id = edge["to_id"] if edge["from_id"] == node_id else edge["from_id"]
            else:
                target_id = edge.to_id if edge.from_id == node_id else edge.from_id
            node = await self.storage.get_node(target_id)
            if node:
                # Handle both dict and object
                if isinstance(node, dict):
                    node_dict = node
                elif hasattr(node, 'to_dict'):
                    node_dict = node.to_dict()
                else:
                    node_dict = node
                
                # Handle both dict and object edges for relationship
                if isinstance(edge, dict):
                    relationship = edge.get("relation", "RELATED")
                    weight = edge.get("weight", 1.0)
                else:
                    relationship = edge.relation.value if hasattr(edge.relation, 'value') else edge.relation
                    weight = getattr(edge, 'weight', 1.0)
                
                related.append({
                    **node_dict,
                    "relationship": relationship,
                    "weight": weight,
                })
        
        return related
    
    async def what_changed(
        self,
        repo: str,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> list[dict]:
        """Get changes in repository over time."""
        # TODO: Implement
        return []
    
    async def add_node(self, node: dict) -> str:
        """Add a node to the graph."""
        # TODO: Implement
        return ""
    
    async def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        metadata: dict = None
    ) -> str:
        """Add an edge between nodes."""
        # TODO: Implement
        return ""
