"""
Concept - A documented research idea in the knowledge graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


ConceptType = Literal["foundational", "experimental", "meta", "tooling"]
ConceptStatus = Literal["draft", "active", "stable", "deprecated"]


@dataclass
class Concept:
    """
    A concept in the knowledge graph.
    
    Represents a documented research idea with relationships to other concepts.
    """
    
    id: str
    type: ConceptType
    definition: str
    status: ConceptStatus = "active"
    significance: Optional[str] = None  # LOW, MEDIUM, HIGH, CRITICAL
    files: list[dict] = field(default_factory=list)  # [{path, type}]
    tags: list[str] = field(default_factory=list)
    relates_to: list[str] = field(default_factory=list)
    _content: Optional[str] = field(default=None, repr=False)
    _cip_path: Optional[Path] = field(default=None, repr=False)
    
    @classmethod
    def from_dict(cls, concept_id: str, data: dict, cip_path: Path) -> "Concept":
        """Create Concept from knowledge-graph.yaml entry."""
        return cls(
            id=concept_id,
            type=data.get("type", "foundational"),
            definition=data.get("definition", ""),
            status=data.get("status", "active"),
            significance=data.get("significance"),
            files=data.get("files", []),
            tags=data.get("tags", []),
            relates_to=data.get("relates_to", []),
            _cip_path=cip_path,
        )
    
    def load_content(self) -> str:
        """Load full content from concept files."""
        if self._content is not None:
            return self._content
        
        if not self._cip_path or not self.files:
            return self.definition
        
        content_parts = []
        for file_ref in self.files:
            file_path = self._cip_path / file_ref["path"]
            if file_path.exists():
                content_parts.append(file_path.read_text())
        
        self._content = "\n\n---\n\n".join(content_parts) if content_parts else self.definition
        return self._content
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "definition": self.definition,
            "status": self.status,
            "significance": self.significance,
            "files": self.files,
            "tags": self.tags,
            "relates_to": self.relates_to,
        }
    
    def to_context(self, include_content: bool = True) -> dict:
        """Convert to context format for agents."""
        ctx = {
            "id": self.id,
            "type": self.type,
            "definition": self.definition,
            "tags": self.tags,
        }
        if include_content:
            ctx["content"] = self.load_content()
        return ctx
