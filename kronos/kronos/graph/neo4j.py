"""
Neo4j Graph Backend

Production-grade graph storage using Neo4j.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from datetime import datetime

from .base import GraphBackendBase
from ..types import RepoNode, RepoEdge, NodeType, RelationType

logger = logging.getLogger(__name__)


class Neo4jGraphBackend(GraphBackendBase):
    """
    Neo4j-based graph backend.
    
    Full-featured graph database for production use.
    Requires Neo4j server running.
    """
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize Neo4j backend.
        
        Args:
            uri: Neo4j bolt URI (or just password if using default)
            user: Username
            password: Password
        """
        # Parse URI - could be full URI or just db path for compat
        if uri.startswith("bolt://") or uri.startswith("neo4j://"):
            self.uri = uri
        else:
            self.uri = "bolt://localhost:7687"
            password = uri  # Assume it's the password
        
        self.user = user
        self.password = password
        self.driver = None
        
        logger.info(f"Neo4j graph backend: {self.uri}")
    
    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            from neo4j import AsyncGraphDatabase
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            await self.driver.verify_connectivity()
            logger.info("Neo4j connection established")
        except ImportError:
            raise ImportError(
                "neo4j package not installed. "
                "Install with: pip install neo4j"
            )
    
    async def close(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
    
    async def create_node(self, node: RepoNode) -> None:
        """Create a node in Neo4j."""
        async with self.driver.session() as session:
            await session.run(
                """
                MERGE (n:RepoNode {id: $id})
                SET n.type = $type,
                    n.path = $path,
                    n.content = $content,
                    n.name = $name,
                    n.language = $language,
                    n.line_start = $line_start,
                    n.line_end = $line_end,
                    n.created_at = $created_at,
                    n.updated_at = $updated_at,
                    n.commit_sha = $commit_sha,
                    n.description = $description,
                    n.semantic_scope = $semantic_scope,
                    n.proficiency_level = $proficiency_level
                """,
                id=node.id,
                type=node.type.value,
                path=node.path,
                content=node.content,
                name=node.name,
                language=node.language,
                line_start=node.line_start,
                line_end=node.line_end,
                created_at=node.created_at.isoformat(),
                updated_at=node.updated_at.isoformat() if node.updated_at else None,
                commit_sha=node.commit_sha,
                description=node.description,
                semantic_scope=node.semantic_scope,
                proficiency_level=node.proficiency_level,
            )
    
    async def get_node(self, node_id: str) -> Optional[RepoNode]:
        """Get a node by ID."""
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (n:RepoNode {id: $id}) RETURN n",
                id=node_id,
            )
            record = await result.single()
            
            if record is None:
                return None
            
            return self._record_to_node(record["n"])
    
    def _record_to_node(self, record) -> RepoNode:
        """Convert Neo4j record to RepoNode."""
        return RepoNode(
            id=record["id"],
            type=NodeType(record["type"]),
            path=record["path"],
            content=record.get("content", ""),
            name=record.get("name"),
            language=record.get("language"),
            line_start=record.get("line_start"),
            line_end=record.get("line_end"),
            created_at=datetime.fromisoformat(record["created_at"]),
            updated_at=datetime.fromisoformat(record["updated_at"]) if record.get("updated_at") else None,
            commit_sha=record.get("commit_sha"),
            description=record.get("description"),
            semantic_scope=record.get("semantic_scope"),
            proficiency_level=record.get("proficiency_level"),
        )
    
    async def update_node(self, node: RepoNode) -> None:
        """Update a node."""
        await self.create_node(node)  # MERGE handles upsert
    
    async def delete_node(self, node_id: str) -> None:
        """Delete a node and its relationships."""
        async with self.driver.session() as session:
            await session.run(
                "MATCH (n:RepoNode {id: $id}) DETACH DELETE n",
                id=node_id,
            )
    
    async def create_edge(self, edge: RepoEdge) -> None:
        """Create a relationship."""
        async with self.driver.session() as session:
            await session.run(
                f"""
                MATCH (from:RepoNode {{id: $from_id}})
                MATCH (to:RepoNode {{id: $to_id}})
                MERGE (from)-[r:{edge.relation.value}]->(to)
                SET r.id = $edge_id,
                    r.weight = $weight,
                    r.created_at = $created_at
                """,
                from_id=edge.from_id,
                to_id=edge.to_id,
                edge_id=edge.id,
                weight=edge.weight,
                created_at=edge.created_at.isoformat(),
            )
    
    async def get_edges(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        direction: str = "both",
    ) -> List[RepoEdge]:
        """Get relationships for a node."""
        type_filter = ""
        if relation_types:
            types = "|".join(r.value for r in relation_types)
            type_filter = f":{types}"
        
        if direction == "out":
            pattern = f"(n)-[r{type_filter}]->(m)"
        elif direction == "in":
            pattern = f"(n)<-[r{type_filter}]-(m)"
        else:
            pattern = f"(n)-[r{type_filter}]-(m)"
        
        async with self.driver.session() as session:
            result = await session.run(
                f"""
                MATCH {pattern}
                WHERE n.id = $id
                RETURN r, startNode(r).id as from_id, endNode(r).id as to_id, type(r) as rel_type
                """,
                id=node_id,
            )
            
            edges = []
            async for record in result:
                r = record["r"]
                edges.append(RepoEdge(
                    id=r.get("id", ""),
                    from_id=record["from_id"],
                    to_id=record["to_id"],
                    relation=RelationType(record["rel_type"]),
                    weight=r.get("weight", 1.0),
                    created_at=datetime.fromisoformat(r["created_at"]) if r.get("created_at") else datetime.now(),
                ))
            
            return edges
    
    async def delete_edge(self, edge_id: str) -> None:
        """Delete a relationship by ID."""
        async with self.driver.session() as session:
            await session.run(
                "MATCH ()-[r {id: $id}]-() DELETE r",
                id=edge_id,
            )
    
    async def get_neighbors(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 1,
    ) -> List[RepoNode]:
        """Get neighboring nodes."""
        type_filter = ""
        if relation_types:
            types = "|".join(r.value for r in relation_types)
            type_filter = f":{types}"
        
        async with self.driver.session() as session:
            result = await session.run(
                f"""
                MATCH (n:RepoNode {{id: $id}})-[{type_filter}*1..{max_depth}]-(m:RepoNode)
                RETURN DISTINCT m
                """,
                id=node_id,
            )
            
            nodes = []
            async for record in result:
                nodes.append(self._record_to_node(record["m"]))
            
            return nodes
    
    async def trace_path(
        self,
        node_id: str,
        relation_types: List[RelationType],
        direction: str = "both",
        max_depth: int = 10,
    ) -> List[RepoNode]:
        """Trace a path through specific relationships."""
        types = "|".join(r.value for r in relation_types)
        
        if direction == "forward":
            pattern = f"-[:{types}]->"
        elif direction == "backward":
            pattern = f"<-[:{types}]-"
        else:
            pattern = f"-[:{types}]-"
        
        async with self.driver.session() as session:
            result = await session.run(
                f"""
                MATCH path = (n:RepoNode {{id: $id}}){pattern}*(m:RepoNode)
                WHERE length(path) <= $max_depth
                UNWIND nodes(path) as node
                RETURN DISTINCT node
                """,
                id=node_id,
                max_depth=max_depth,
            )
            
            nodes = []
            async for record in result:
                nodes.append(self._record_to_node(record["node"]))
            
            return nodes
    
    async def health_check(self) -> bool:
        """Check Neo4j health."""
        try:
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            return True
        except Exception:
            return False
