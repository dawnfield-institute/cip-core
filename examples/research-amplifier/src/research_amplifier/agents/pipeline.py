"""
Agent Pipeline - Orchestrates Progressive-Critical post generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json

from research_amplifier.mitosis.assembler import AssembledContext
from research_amplifier.agents.generation import GenerationAgent, GeneratedPost
from research_amplifier.agents.critique import CritiqueAgent, CritiqueResult


@dataclass
class PipelineResult:
    """Result of running the agent pipeline."""
    
    success: bool
    post: Optional[GeneratedPost]
    iterations: int
    critique_history: list[CritiqueResult]
    error: Optional[str] = None
    
    def to_json(self) -> str:
        """Export as JSON for PR creation."""
        if not self.post:
            return json.dumps({"success": False, "error": self.error})
        
        return json.dumps({
            "post_id": self.post.post_id,
            "entry_id": self.post.entry_id,
            "generated_at": self.post.generated_at,
            "platforms": {
                "twitter": {
                    "content": self.post.twitter_content,
                    "character_count": len(self.post.twitter_content),
                },
                "linkedin": {
                    "content": self.post.linkedin_content,
                }
            },
            "metadata": {
                "topics": self.post.topics,
                "tone": self.post.tone,
                "iterations": self.iterations,
            },
            "critique_results": {
                "all_checks_passed": self.success,
                "final_critique": self.critique_history[-1].to_dict() if self.critique_history else None,
            }
        }, indent=2)


class AgentPipeline:
    """
    Orchestrates the Progressive-Critical pipeline for post generation.
    
    Flow:
    1. Context Assembly (already done via Mitosis)
    2. Generation (Progressive - creates initial draft)
    3. Critique (Critical - validates quality)
    4. Refinement loop (max iterations)
    5. Output for PR creation
    """
    
    def __init__(
        self,
        generation_agent: Optional[GenerationAgent] = None,
        critique_agent: Optional[CritiqueAgent] = None,
        max_iterations: int = 3,
    ):
        self.generation = generation_agent or GenerationAgent()
        self.critique = critique_agent or CritiqueAgent()
        self.max_iterations = max_iterations
    
    def run(self, context: AssembledContext) -> PipelineResult:
        """
        Run the full pipeline on assembled context.
        
        Args:
            context: Assembled context from Mitosis
        
        Returns:
            PipelineResult with generated post or error
        """
        critique_history = []
        current_post = None
        
        for iteration in range(self.max_iterations):
            # Generate or refine
            if current_post is None:
                current_post = self.generation.generate(context)
            else:
                # Get feedback from last critique
                feedback = critique_history[-1].compile_feedback()
                current_post = self.generation.refine(current_post, feedback, context)
            
            # Critique
            critique_result = self.critique.evaluate(current_post, context)
            critique_history.append(critique_result)
            
            if critique_result.passed:
                return PipelineResult(
                    success=True,
                    post=current_post,
                    iterations=iteration + 1,
                    critique_history=critique_history,
                )
        
        # Max iterations reached - return best effort
        return PipelineResult(
            success=False,
            post=current_post,
            iterations=self.max_iterations,
            critique_history=critique_history,
            error=f"Did not pass critique after {self.max_iterations} iterations",
        )
    
    def run_dry(self, context: AssembledContext) -> GeneratedPost:
        """
        Run generation only, skip critique (for testing).
        """
        return self.generation.generate(context)
