"""
Context Assembler - Dynamic context assembly from knowledge graph.

Mitosis is the process of dividing and assembling relevant context
for agent consumption. Named for the biological process of cell division,
it represents how knowledge is selected and packaged for specific tasks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from research_amplifier.knowledge.graph import KnowledgeGraph
from research_amplifier.knowledge.entries import Entry


@dataclass
class AssembledContext:
    """Context assembled for agent consumption."""
    
    entry: dict
    concepts: dict[str, dict]
    relationships: list[dict]
    recent_entries: list[dict]
    token_estimate: int
    metadata: dict = field(default_factory=dict)
    
    def to_prompt_section(self) -> str:
        """Format context as a prompt section for LLMs."""
        sections = []
        
        # Entry section
        sections.append("## Research Event\n")
        sections.append(f"**ID:** {self.entry['entry_id']}")
        sections.append(f"**Type:** {self.entry['type']}")
        sections.append(f"**Significance:** {self.entry['significance']}")
        sections.append(f"\n**Technical Summary:** {self.entry['summary']['technical']}")
        sections.append(f"\n**Accessible Summary:** {self.entry['summary']['accessible']}")
        sections.append(f"\n**One-liner:** {self.entry['summary']['one_liner']}")
        
        if self.entry.get('guidance'):
            g = self.entry['guidance']
            sections.append(f"\n**Angle:** {g.get('angle', 'N/A')}")
            sections.append(f"**Hooks:** {', '.join(g.get('hooks', []))}")
            sections.append(f"**Avoid:** {g.get('avoid', 'N/A')}")
            sections.append(f"**Tone:** {g.get('tone', 'thoughtful')}")
        
        # Concepts section
        if self.concepts:
            sections.append("\n## Related Concepts\n")
            for concept_id, concept in self.concepts.items():
                sections.append(f"### {concept_id}")
                sections.append(f"**Definition:** {concept['definition']}")
                sections.append(f"**Tags:** {', '.join(concept.get('tags', []))}")
                if 'content' in concept and concept['content'] != concept['definition']:
                    # Truncate long content
                    content = concept['content']
                    if len(content) > 1000:
                        content = content[:1000] + "..."
                    sections.append(f"\n{content}")
                sections.append("")
        
        # Recent entries for continuity
        if self.recent_entries:
            sections.append("\n## Recent Posts (for continuity)\n")
            for entry in self.recent_entries[:3]:
                sections.append(f"- {entry['summary']['one_liner']}")
        
        return "\n".join(sections)


class ContextAssembler:
    """
    Assembles context from knowledge graph for agent consumption.
    
    The assembler traverses the knowledge graph starting from an entry,
    loads related concepts to the specified depth, and packages everything
    into a structured context suitable for LLM prompts.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    @classmethod
    def from_repo(cls, repo_path: str) -> "ContextAssembler":
        """Create assembler from repository path."""
        kg = KnowledgeGraph.load(repo_path)
        return cls(kg)
    
    def assemble(
        self,
        entry_id: str,
        depth: int = 1,
        include_recent: int = 5,
        max_tokens: int = 10000,
    ) -> AssembledContext:
        """
        Assemble context for an entry.
        
        Args:
            entry_id: The entry to assemble context for
            depth: How many relationship hops to traverse
            include_recent: Number of recent entries to include
            max_tokens: Approximate token budget
        
        Returns:
            AssembledContext with entry, concepts, and metadata
        """
        # Load entry
        entry = self.kg.get_entry(entry_id)
        
        # Get connected concepts from entry
        connected_ids = entry.significance.connects_to
        
        # Expand to related concepts
        all_concept_ids = set(connected_ids)
        for concept_id in connected_ids:
            if concept_id in self.kg.concepts:
                related = self.kg.get_related(concept_id, depth=depth)
                all_concept_ids.update(related)
        
        # Load concepts with content
        concepts = {}
        token_count = 0
        
        for concept_id in all_concept_ids:
            if concept_id not in self.kg.concepts:
                continue
            
            concept = self.kg.get_concept(concept_id)
            ctx = concept.to_context(include_content=True)
            
            # Estimate tokens (rough: 4 chars per token)
            concept_tokens = len(str(ctx)) // 4
            if token_count + concept_tokens > max_tokens * 0.7:
                # Budget exceeded, include definition only
                ctx = concept.to_context(include_content=False)
            
            concepts[concept_id] = ctx
            token_count += len(str(ctx)) // 4
        
        # Get recent entries for continuity
        recent = self.kg.get_entries(days=30, unposted_only=False)
        recent = [e for e in recent if e.entry_id != entry_id][:include_recent]
        
        # Build relationships list
        relationships = []
        for rel in self.kg.relationships:
            if rel.source in all_concept_ids or rel.target in all_concept_ids:
                relationships.append({
                    "source": rel.source,
                    "target": rel.target,
                    "type": rel.type,
                    "strength": rel.strength,
                })
        
        return AssembledContext(
            entry=entry.to_context(),
            concepts=concepts,
            relationships=relationships,
            recent_entries=[e.to_context() for e in recent],
            token_estimate=token_count,
            metadata={
                "depth": depth,
                "concepts_loaded": len(concepts),
                "budget_used": token_count / max_tokens,
            }
        )
    
    def assemble_for_concepts(
        self,
        concept_ids: list[str],
        depth: int = 1,
        max_tokens: int = 8000,
    ) -> dict:
        """
        Assemble context for a list of concepts (without entry).
        
        Useful for ad-hoc queries or exploration.
        """
        all_concept_ids = set(concept_ids)
        for concept_id in concept_ids:
            if concept_id in self.kg.concepts:
                related = self.kg.get_related(concept_id, depth=depth)
                all_concept_ids.update(related)
        
        concepts = {}
        for concept_id in all_concept_ids:
            if concept_id in self.kg.concepts:
                concept = self.kg.get_concept(concept_id)
                concepts[concept_id] = concept.to_context(include_content=True)
        
        return {
            "concepts": concepts,
            "relationships": [
                {
                    "source": r.source,
                    "target": r.target,
                    "type": r.type,
                }
                for r in self.kg.relationships
                if r.source in all_concept_ids or r.target in all_concept_ids
            ]
        }
