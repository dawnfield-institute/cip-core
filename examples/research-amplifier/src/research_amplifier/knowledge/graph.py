"""
Knowledge Graph - Core data structure for CIP v2 semantic organization.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from research_amplifier.knowledge.concepts import Concept
from research_amplifier.knowledge.entries import Entry, EntryManager


@dataclass
class Relationship:
    """A relationship between two concepts."""
    source: str
    target: str
    type: str  # validates, extends, depends_on, contradicts, implements
    strength: float = 1.0
    description: str = ""


@dataclass
class KnowledgeGraph:
    """
    CIP v2 Knowledge Graph - semantic organization of research knowledge.
    
    Loads from a repository's cip/ directory structure:
    - cip/knowledge-graph.yaml (master index)
    - cip/concepts/*.md (concept documentation)
    - cip/entries/*.json (research events)
    """
    
    repo_path: Path
    concepts: dict[str, Concept] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    _entry_manager: Optional[EntryManager] = field(default=None, repr=False)
    
    @classmethod
    def load(cls, repo_path: str | Path) -> "KnowledgeGraph":
        """Load knowledge graph from repository."""
        repo_path = Path(repo_path)
        cip_path = repo_path / "cip"
        
        if not cip_path.exists():
            raise FileNotFoundError(f"No cip/ directory found in {repo_path}")
        
        kg_file = cip_path / "knowledge-graph.yaml"
        if not kg_file.exists():
            raise FileNotFoundError(f"No knowledge-graph.yaml found in {cip_path}")
        
        with open(kg_file) as f:
            data = yaml.safe_load(f)
        
        kg = cls(repo_path=repo_path)
        kg.metadata = data.get("metadata", {})
        
        # Load concepts
        for concept_id, concept_data in data.get("concepts", {}).items():
            kg.concepts[concept_id] = Concept.from_dict(concept_id, concept_data, cip_path)
        
        # Load relationships
        for rel_data in data.get("relationships", []):
            kg.relationships.append(Relationship(**rel_data))
        
        # Also extract implicit relationships from relates_to
        for concept_id, concept in kg.concepts.items():
            for related_id in concept.relates_to:
                # Check if explicit relationship exists
                explicit = any(
                    r.source == concept_id and r.target == related_id
                    for r in kg.relationships
                )
                if not explicit:
                    kg.relationships.append(Relationship(
                        source=concept_id,
                        target=related_id,
                        type="relates_to",
                        strength=0.5
                    ))
        
        # Initialize entry manager
        kg._entry_manager = EntryManager(cip_path / "entries")
        
        return kg
    
    def get_concept(self, concept_id: str) -> Concept:
        """Get a concept by ID."""
        if concept_id not in self.concepts:
            raise KeyError(f"Concept not found: {concept_id}")
        return self.concepts[concept_id]
    
    def get_related(self, concept_id: str, depth: int = 1) -> list[str]:
        """Get related concept IDs up to specified depth."""
        if depth < 1:
            return []
        
        related = set()
        to_process = {concept_id}
        
        for _ in range(depth):
            next_level = set()
            for cid in to_process:
                # Find all relationships involving this concept
                for rel in self.relationships:
                    if rel.source == cid and rel.target not in related:
                        related.add(rel.target)
                        next_level.add(rel.target)
                    elif rel.target == cid and rel.source not in related:
                        related.add(rel.source)
                        next_level.add(rel.source)
            to_process = next_level
        
        related.discard(concept_id)
        return list(related)
    
    def search(self, query: str, limit: int = 5) -> list[tuple[str, float]]:
        """
        Search concepts by query string.
        
        Returns list of (concept_id, relevance_score) tuples.
        
        Note: v1 uses keyword matching. v2 will add vector embeddings.
        """
        query_lower = query.lower()
        query_terms = set(query_lower.split())
        
        scores = []
        for concept_id, concept in self.concepts.items():
            score = 0.0
            
            # Check definition
            if query_lower in concept.definition.lower():
                score += 0.5
            
            # Check tags
            matching_tags = query_terms & set(concept.tags)
            score += len(matching_tags) * 0.3
            
            # Check ID
            if query_lower in concept_id.lower():
                score += 0.4
            
            # Term overlap in definition
            def_terms = set(concept.definition.lower().split())
            overlap = len(query_terms & def_terms) / max(len(query_terms), 1)
            score += overlap * 0.3
            
            if score > 0:
                scores.append((concept_id, min(score, 1.0)))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]
    
    def get_entries(self, days: int = 7, unposted_only: bool = True) -> list[Entry]:
        """Get recent research entries."""
        if self._entry_manager is None:
            return []
        return self._entry_manager.get_recent(days=days, unposted_only=unposted_only)
    
    def get_entry(self, entry_id: str) -> Entry:
        """Get a specific entry by ID."""
        if self._entry_manager is None:
            raise RuntimeError("Entry manager not initialized")
        return self._entry_manager.get(entry_id)
    
    def mark_posted(self, entry_id: str, post_id: str, platform: str = "twitter") -> None:
        """Mark an entry as posted."""
        if self._entry_manager is None:
            raise RuntimeError("Entry manager not initialized")
        self._entry_manager.mark_posted(entry_id, post_id, platform)
    
    def validate(self) -> list[str]:
        """Validate knowledge graph integrity. Returns list of issues."""
        issues = []
        
        # Check all relates_to references exist
        for concept_id, concept in self.concepts.items():
            for related_id in concept.relates_to:
                if related_id not in self.concepts:
                    issues.append(f"Concept '{concept_id}' references unknown concept '{related_id}'")
        
        # Check all relationship references exist
        for rel in self.relationships:
            if rel.source not in self.concepts:
                issues.append(f"Relationship source '{rel.source}' not found")
            if rel.target not in self.concepts:
                issues.append(f"Relationship target '{rel.target}' not found")
        
        # Check concept files exist
        for concept_id, concept in self.concepts.items():
            for file_ref in concept.files:
                file_path = self.repo_path / "cip" / file_ref["path"]
                if not file_path.exists():
                    issues.append(f"Concept '{concept_id}' references missing file: {file_ref['path']}")
        
        return issues
