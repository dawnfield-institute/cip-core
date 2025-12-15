"""
Research Amplifier - AI-powered social media automation for research communication.

Human curation + AI understanding + Agentic generation = Authentic automated presence
"""

__version__ = "0.1.0"

from research_amplifier.knowledge.graph import KnowledgeGraph
from research_amplifier.knowledge.entries import Entry, EntryManager
from research_amplifier.mitosis.assembler import ContextAssembler
from research_amplifier.agents.pipeline import AgentPipeline

__all__ = [
    "KnowledgeGraph",
    "Entry",
    "EntryManager", 
    "ContextAssembler",
    "AgentPipeline",
]
