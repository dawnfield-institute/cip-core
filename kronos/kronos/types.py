"""
Kronos Type Definitions

Core data structures for repository knowledge graphs.
Adapted from GRIMM's Kronos for CIP repository understanding.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any


class NodeType(str, Enum):
    """Types of nodes in a repository knowledge graph."""
    
    # Code entities
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"
    FUNCTION = "FUNCTION"
    CLASS = "CLASS"
    METHOD = "METHOD"
    MODULE = "MODULE"
    VARIABLE = "VARIABLE"
    
    # Documentation
    DOCUMENT = "DOCUMENT"
    SECTION = "SECTION"
    COMMENT = "COMMENT"
    
    # CIP-specific
    META_YAML = "META_YAML"
    CONCEPT = "CONCEPT"
    
    # Version control
    COMMIT = "COMMIT"
    BRANCH = "BRANCH"
    
    # Abstract
    IDEA = "IDEA"
    PATTERN = "PATTERN"


class RelationType(str, Enum):
    """Types of relationships between nodes."""
    
    # Structural
    CONTAINS = "CONTAINS"  # Parent contains child
    PART_OF = "PART_OF"  # Child is part of parent
    
    # Code relationships
    IMPORTS = "IMPORTS"  # Import dependency
    EXPORTS = "EXPORTS"  # Exported symbol
    CALLS = "CALLS"  # Function call
    CALLED_BY = "CALLED_BY"  # Inverse of CALLS
    INHERITS = "INHERITS"  # Class inheritance
    IMPLEMENTS = "IMPLEMENTS"  # Interface implementation
    REFERENCES = "REFERENCES"  # General reference
    
    # Temporal (from original Kronos)
    FOLLOWS = "FOLLOWS"  # Sequential in time
    PRECEDES = "PRECEDES"  # Inverse of FOLLOWS
    EVOLVES_FROM = "EVOLVES_FROM"  # Idea/code evolution
    EVOLVES_TO = "EVOLVES_TO"  # Future evolution
    
    # Semantic (from original Kronos)
    RELATES_TO = "RELATES_TO"  # General semantic connection
    SUPPORTS = "SUPPORTS"  # Supporting evidence
    CONTRADICTS = "CONTRADICTS"  # Opposing information
    RESONATES_WITH = "RESONATES_WITH"  # High similarity
    
    # Documentation
    DOCUMENTS = "DOCUMENTS"  # Doc describes code
    DOCUMENTED_BY = "DOCUMENTED_BY"  # Code has documentation
    
    # Causal
    CAUSES = "CAUSES"
    CAUSED_BY = "CAUSED_BY"


@dataclass
class RepoNode:
    """
    A node in the repository knowledge graph.
    
    Represents files, functions, classes, concepts, etc.
    """
    
    id: str
    type: NodeType
    path: str  # Repository path (e.g., "src/main.py")
    content: str  # Text content or summary
    embedding: Optional[List[float]] = None  # Vector embedding
    
    # Metadata
    name: Optional[str] = None  # Symbol name
    language: Optional[str] = None  # Programming language
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    
    # Temporal
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    commit_sha: Optional[str] = None
    
    # CIP-specific
    description: Optional[str] = None
    semantic_scope: Optional[str] = None
    proficiency_level: Optional[str] = None
    
    # Extra metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "path": self.path,
            "content": self.content,
            "embedding": self.embedding,
            "name": self.name,
            "language": self.language,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "commit_sha": self.commit_sha,
            "description": self.description,
            "semantic_scope": self.semantic_scope,
            "proficiency_level": self.proficiency_level,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RepoNode:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            type=NodeType(data["type"]),
            path=data["path"],
            content=data["content"],
            embedding=data.get("embedding"),
            name=data.get("name"),
            language=data.get("language"),
            line_start=data.get("line_start"),
            line_end=data.get("line_end"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            commit_sha=data.get("commit_sha"),
            description=data.get("description"),
            semantic_scope=data.get("semantic_scope"),
            proficiency_level=data.get("proficiency_level"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class RepoEdge:
    """An edge connecting two nodes in the graph."""
    
    id: str
    from_id: str
    to_id: str
    relation: RelationType
    weight: float = 1.0
    
    # Temporal
    created_at: datetime = field(default_factory=datetime.now)
    
    # Context
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "relation": self.relation.value,
            "weight": self.weight,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RepoEdge:
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            from_id=data["from_id"],
            to_id=data["to_id"],
            relation=RelationType(data["relation"]),
            weight=data.get("weight", 1.0),
            created_at=datetime.fromisoformat(data["created_at"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class QueryResult:
    """Result from a semantic query."""
    
    node: RepoNode
    score: float  # Similarity/relevance score
    path_strength: Optional[float] = None  # Graph-expanded strength
    expanded_via_graph: bool = False
    
    @property
    def strength(self) -> float:
        """Overall result strength."""
        return self.path_strength if self.path_strength is not None else self.score
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "node": self.node.to_dict(),
            "score": self.score,
            "path_strength": self.path_strength,
            "strength": self.strength,
            "expanded_via_graph": self.expanded_via_graph,
        }
