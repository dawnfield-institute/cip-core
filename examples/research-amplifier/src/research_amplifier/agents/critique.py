"""
Critique Agent - Validates post quality using Progressive-Critical pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from research_amplifier.mitosis.assembler import AssembledContext
from research_amplifier.agents.generation import GeneratedPost


@dataclass
class Check:
    """A single critique check result."""
    name: str
    passed: bool
    score: float  # 0.0 - 1.0
    feedback: str


@dataclass
class CritiqueResult:
    """Result of critique evaluation."""
    
    passed: bool
    checks: dict[str, Check]
    overall_score: float
    
    def compile_feedback(self) -> str:
        """Compile feedback for refinement."""
        failed_checks = [c for c in self.checks.values() if not c.passed]
        if not failed_checks:
            return "All checks passed."
        
        feedback_lines = ["Please address the following issues:\n"]
        for check in failed_checks:
            feedback_lines.append(f"- **{check.name}**: {check.feedback}")
        
        return "\n".join(feedback_lines)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "passed": self.passed,
            "overall_score": self.overall_score,
            "checks": {
                name: {
                    "passed": check.passed,
                    "score": check.score,
                    "feedback": check.feedback,
                }
                for name, check in self.checks.items()
            }
        }


class CritiqueAgent:
    """
    Evaluates generated posts for quality and authenticity.
    
    Implements the "Critical" side of Progressive-Critical equilibrium,
    ensuring posts meet quality standards before human review.
    """
    
    def __init__(
        self,
        min_score: float = 0.7,
        use_llm_critique: bool = False,
        model: str = "claude-sonnet-4-20250514",
    ):
        self.min_score = min_score
        self.use_llm_critique = use_llm_critique
        self.model = model
    
    def evaluate(self, post: GeneratedPost, context: AssembledContext) -> CritiqueResult:
        """
        Evaluate a generated post.
        
        Args:
            post: The generated post to evaluate
            context: Original context for comparison
        
        Returns:
            CritiqueResult with pass/fail and feedback
        """
        checks = {}
        
        # Run all checks
        checks["accuracy"] = self._check_accuracy(post, context)
        checks["accessibility"] = self._check_accessibility(post)
        checks["tone"] = self._check_tone(post, context)
        checks["platform_fit"] = self._check_platform_fit(post)
        checks["no_hype"] = self._check_no_hype(post)
        
        # Calculate overall score
        scores = [c.score for c in checks.values()]
        overall_score = sum(scores) / len(scores)
        
        # Determine pass/fail
        all_passed = all(c.passed for c in checks.values())
        score_passed = overall_score >= self.min_score
        
        return CritiqueResult(
            passed=all_passed and score_passed,
            checks=checks,
            overall_score=overall_score,
        )
    
    def _check_accuracy(self, post: GeneratedPost, context: AssembledContext) -> Check:
        """Check technical accuracy against source material."""
        entry = context.entry
        
        # Check that key terms from entry appear in posts
        technical_terms = set(entry["summary"]["technical"].lower().split())
        twitter_terms = set(post.twitter_content.lower().split())
        linkedin_terms = set(post.linkedin_content.lower().split())
        
        # Filter to meaningful terms (>4 chars)
        technical_terms = {t for t in technical_terms if len(t) > 4}
        
        if not technical_terms:
            return Check(
                name="accuracy",
                passed=True,
                score=1.0,
                feedback="No specific terms to verify."
            )
        
        all_post_terms = twitter_terms | linkedin_terms
        overlap = technical_terms & all_post_terms
        coverage = len(overlap) / len(technical_terms) if technical_terms else 1.0
        
        # Relaxed threshold - we don't need exact term matching
        passed = coverage >= 0.2 or len(overlap) >= 2
        
        return Check(
            name="accuracy",
            passed=passed,
            score=min(coverage * 2, 1.0),  # Scale up since exact matching is hard
            feedback="Posts should reference key concepts from the research." if not passed else "Good coverage of key terms."
        )
    
    def _check_accessibility(self, post: GeneratedPost) -> Check:
        """Check that posts are accessible to general audience."""
        # Simple heuristics for accessibility
        issues = []
        
        # Check sentence length in LinkedIn
        sentences = post.linkedin_content.split(".")
        long_sentences = [s for s in sentences if len(s.split()) > 30]
        if long_sentences:
            issues.append("Some sentences are too long")
        
        # Check for jargon without explanation
        jargon_words = ["eigenvalue", "manifold", "topology", "hamiltonian", "lagrangian"]
        linkedin_lower = post.linkedin_content.lower()
        unexplained_jargon = [w for w in jargon_words if w in linkedin_lower]
        
        # It's okay to use jargon if the post is long enough to explain
        if unexplained_jargon and len(post.linkedin_content) < 200:
            issues.append(f"Technical terms may need context: {', '.join(unexplained_jargon)}")
        
        score = 1.0 - (len(issues) * 0.2)
        
        return Check(
            name="accessibility",
            passed=score >= 0.6,
            score=max(score, 0.0),
            feedback="; ".join(issues) if issues else "Good accessibility."
        )
    
    def _check_tone(self, post: GeneratedPost, context: AssembledContext) -> Check:
        """Check tone consistency with guidance."""
        suggested_tone = context.entry.get("guidance", {}).get("tone", "thoughtful")
        
        # Check for tone mismatches
        hype_indicators = ["revolutionary", "groundbreaking", "game-changing", "incredible"]
        humble_indicators = ["exploring", "investigating", "suggests", "appears"]
        
        content = (post.twitter_content + " " + post.linkedin_content).lower()
        
        hype_count = sum(1 for word in hype_indicators if word in content)
        humble_count = sum(1 for word in humble_indicators if word in content)
        
        if suggested_tone == "thoughtful" and hype_count > humble_count:
            return Check(
                name="tone",
                passed=False,
                score=0.4,
                feedback="Tone is too promotional for 'thoughtful' guidance. Use more measured language."
            )
        
        return Check(
            name="tone",
            passed=True,
            score=0.9,
            feedback="Tone aligns with guidance."
        )
    
    def _check_platform_fit(self, post: GeneratedPost) -> Check:
        """Check platform-specific requirements."""
        issues = []
        
        # Twitter length
        if len(post.twitter_content) > 280:
            issues.append(f"Twitter post too long: {len(post.twitter_content)}/280 chars")
        elif len(post.twitter_content) < 50:
            issues.append("Twitter post may be too short to be engaging")
        
        # LinkedIn length
        if len(post.linkedin_content) < 100:
            issues.append("LinkedIn post is quite short")
        elif len(post.linkedin_content) > 3000:
            issues.append("LinkedIn post may be too long")
        
        # Check Twitter doesn't start with "I"
        if post.twitter_content.strip().startswith("I "):
            issues.append("Twitter post starts with 'I' - consider leading with the insight")
        
        score = 1.0 - (len(issues) * 0.25)
        
        return Check(
            name="platform_fit",
            passed=len(issues) == 0,
            score=max(score, 0.0),
            feedback="; ".join(issues) if issues else "Good platform fit."
        )
    
    def _check_no_hype(self, post: GeneratedPost) -> Check:
        """Check for hype language that should be avoided."""
        hype_phrases = [
            "breakthrough",
            "game-changing", 
            "revolutionary",
            "world-first",
            "unprecedented",
            "mind-blowing",
            "incredible",
            "amazing discovery",
        ]
        
        content = (post.twitter_content + " " + post.linkedin_content).lower()
        found_hype = [phrase for phrase in hype_phrases if phrase in content]
        
        if found_hype:
            return Check(
                name="no_hype",
                passed=False,
                score=0.3,
                feedback=f"Avoid hype language: {', '.join(found_hype)}. Use measured, precise language."
            )
        
        return Check(
            name="no_hype",
            passed=True,
            score=1.0,
            feedback="No hype language detected."
        )
