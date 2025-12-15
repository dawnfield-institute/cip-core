"""
SQLite Graph Backend

Simple graph storage using SQLite for development and small repos.
"""

from __future__ import annotations

import logging
import sqlite3
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .base import GraphBackendBase
from ..types import RepoNode, RepoEdge, NodeType, RelationType

logger = logging.getLogger(__name__)


class SQLiteGraphBackend(GraphBackendBase):
    """
    SQLite-based graph backend.
    
    Simple and portable, good for development and small repositories.
    """
    
    def __init__(self, db_path: str = "kronos.db"):
        """
        Initialize SQLite backend.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        logger.info(f"SQLite graph backend: {db_path}")
    
    async def connect(self) -> None:
        """Create connection and initialize schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                content TEXT,
                name TEXT,
                language TEXT,
                line_start INTEGER,
                line_end INTEGER,
                created_at TEXT,
                updated_at TEXT,
                commit_sha TEXT,
                description TEXT,
                semantic_scope TEXT,
                proficiency_level TEXT,
                metadata TEXT
            );
            
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                created_at TEXT,
                metadata TEXT,
                FOREIGN KEY (from_id) REFERENCES nodes(id),
                FOREIGN KEY (to_id) REFERENCES nodes(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_nodes_path ON nodes(path);
            CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type);
            CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_id);
            CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_id);
            CREATE INDEX IF NOT EXISTS idx_edges_relation ON edges(relation);
        """)
        self.conn.commit()
        logger.info("SQLite schema initialized")
    
    async def close(self) -> None:
        """Close the connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    async def create_node(self, node: RepoNode) -> None:
        """Create a node."""
        self.conn.execute("""
            INSERT OR REPLACE INTO nodes 
            (id, type, path, content, name, language, line_start, line_end,
             created_at, updated_at, commit_sha, description, semantic_scope,
             proficiency_level, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            node.id,
            node.type.value,
            node.path,
            node.content,
            node.name,
            node.language,
            node.line_start,
            node.line_end,
            node.created_at.isoformat(),
            node.updated_at.isoformat() if node.updated_at else None,
            node.commit_sha,
            node.description,
            node.semantic_scope,
            node.proficiency_level,
            json.dumps(node.metadata),
        ))
        self.conn.commit()
    
    async def get_node(self, node_id: str) -> Optional[RepoNode]:
        """Get a node by ID."""
        cursor = self.conn.execute(
            "SELECT * FROM nodes WHERE id = ?", (node_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_node(row)
    
    def _row_to_node(self, row: sqlite3.Row) -> RepoNode:
        """Convert a database row to a RepoNode."""
        return RepoNode(
            id=row["id"],
            type=NodeType(row["type"]),
            path=row["path"],
            content=row["content"] or "",
            name=row["name"],
            language=row["language"],
            line_start=row["line_start"],
            line_end=row["line_end"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            commit_sha=row["commit_sha"],
            description=row["description"],
            semantic_scope=row["semantic_scope"],
            proficiency_level=row["proficiency_level"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )
    
    async def update_node(self, node: RepoNode) -> None:
        """Update a node."""
        await self.create_node(node)  # UPSERT
    
    async def delete_node(self, node_id: str) -> None:
        """Delete a node and its edges."""
        self.conn.execute("DELETE FROM edges WHERE from_id = ? OR to_id = ?", (node_id, node_id))
        self.conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        self.conn.commit()
    
    async def create_edge(self, edge: RepoEdge) -> None:
        """Create an edge."""
        self.conn.execute("""
            INSERT OR REPLACE INTO edges 
            (id, from_id, to_id, relation, weight, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            edge.id,
            edge.from_id,
            edge.to_id,
            edge.relation.value,
            edge.weight,
            edge.created_at.isoformat(),
            json.dumps(edge.metadata),
        ))
        self.conn.commit()
    
    async def get_edges(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        direction: str = "both",
    ) -> List[RepoEdge]:
        """Get edges for a node."""
        conditions = []
        params = []
        
        if direction in ("out", "both"):
            conditions.append("from_id = ?")
            params.append(node_id)
        if direction in ("in", "both"):
            conditions.append("to_id = ?")
            params.append(node_id)
        
        where = " OR ".join(conditions)
        
        if relation_types:
            types_str = ",".join(f"'{r.value}'" for r in relation_types)
            where = f"({where}) AND relation IN ({types_str})"
        
        cursor = self.conn.execute(f"SELECT * FROM edges WHERE {where}", params)
        
        edges = []
        for row in cursor:
            edges.append(RepoEdge(
                id=row["id"],
                from_id=row["from_id"],
                to_id=row["to_id"],
                relation=RelationType(row["relation"]),
                weight=row["weight"],
                created_at=datetime.fromisoformat(row["created_at"]),
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            ))
        
        return edges
    
    async def delete_edge(self, edge_id: str) -> None:
        """Delete an edge."""
        self.conn.execute("DELETE FROM edges WHERE id = ?", (edge_id,))
        self.conn.commit()
    
    async def get_neighbors(
        self,
        node_id: str,
        relation_types: Optional[List[RelationType]] = None,
        max_depth: int = 1,
    ) -> List[RepoNode]:
        """Get neighboring nodes (BFS)."""
        visited = set()
        current_level = {node_id}
        neighbors = []
        
        for _ in range(max_depth):
            next_level = set()
            
            for nid in current_level:
                if nid in visited:
                    continue
                visited.add(nid)
                
                edges = await self.get_edges(nid, relation_types, "both")
                
                for edge in edges:
                    target = edge.to_id if edge.from_id == nid else edge.from_id
                    if target not in visited:
                        next_level.add(target)
                        node = await self.get_node(target)
                        if node:
                            neighbors.append(node)
            
            current_level = next_level
            if not current_level:
                break
        
        return neighbors
    
    async def trace_path(
        self,
        node_id: str,
        relation_types: List[RelationType],
        direction: str = "both",
        max_depth: int = 10,
    ) -> List[RepoNode]:
        """Trace a path through specific relationships."""
        path = []
        current = node_id
        visited = set()
        
        for _ in range(max_depth):
            if current in visited:
                break
            visited.add(current)
            
            node = await self.get_node(current)
            if node:
                path.append(node)
            
            edges = await self.get_edges(current, relation_types, direction)
            if not edges:
                break
            
            # Follow first matching edge
            edge = edges[0]
            current = edge.to_id if edge.from_id == current else edge.from_id
        
        return path
    
    async def health_check(self) -> bool:
        """Check if backend is healthy."""
        try:
            self.conn.execute("SELECT 1")
            return True
        except Exception:
            return False
