"""
Generation Agent - Creates social media posts from research context.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import hashlib

from research_amplifier.mitosis.assembler import AssembledContext


@dataclass
class GeneratedPost:
    """A generated social media post."""
    
    post_id: str
    entry_id: str
    generated_at: str
    twitter_content: str
    linkedin_content: str
    topics: list[str]
    tone: str
    thread: Optional[list[str]] = None  # For Twitter threads
    
    @classmethod
    def create_id(cls, entry_id: str) -> str:
        """Generate unique post ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_suffix = hashlib.md5(f"{entry_id}{timestamp}".encode()).hexdigest()[:6]
        return f"post_{timestamp}_{hash_suffix}"


class GenerationAgent:
    """
    Generates social media posts from assembled context.
    
    Uses Claude Sonnet 4 to create platform-appropriate content
    that maintains authentic voice while being accessible.
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
        return self._client
    
    def generate(self, context: AssembledContext) -> GeneratedPost:
        """
        Generate posts from context.
        
        Args:
            context: Assembled context from Mitosis
        
        Returns:
            GeneratedPost with Twitter and LinkedIn content
        """
        prompt = self._build_prompt(context)
        
        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_response(response.content[0].text, context)
        except Exception as e:
            # Fallback to template-based generation
            return self._generate_fallback(context, str(e))
    
    def refine(
        self,
        post: GeneratedPost,
        feedback: str,
        context: AssembledContext,
    ) -> GeneratedPost:
        """Refine a post based on critique feedback."""
        prompt = self._build_refinement_prompt(post, feedback, context)
        
        try:
            client = self._get_client()
            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_response(response.content[0].text, context)
        except Exception:
            # Return original if refinement fails
            return post
    
    def _build_prompt(self, context: AssembledContext) -> str:
        """Build generation prompt."""
        context_section = context.to_prompt_section()
        
        return f"""You are a research communicator helping share scientific discoveries on social media.

{context_section}

Generate social media posts for this research event. 

## Requirements

**Twitter (max 280 chars):**
- Lead with the insight, not "I just..."
- Use accessible language
- Include 1-2 relevant emojis if appropriate
- No hashtag spam (0-2 max)

**LinkedIn (2-3 paragraphs):**
- Professional but not stiff
- Explain significance for broader audience
- End with forward-looking statement or question

**Voice Guidelines:**
- Thoughtful, not hype
- Precise, not vague
- Curious, not arrogant
- Human, not robotic

## Output Format

Respond with exactly this format:

TWITTER:
[your tweet here]

LINKEDIN:
[your linkedin post here]

TONE: [one word: thoughtful/excited/reflective/curious]
TOPICS: [comma-separated concept IDs]
"""
    
    def _build_refinement_prompt(
        self,
        post: GeneratedPost,
        feedback: str,
        context: AssembledContext,
    ) -> str:
        """Build refinement prompt."""
        return f"""Refine this social media post based on critique feedback.

## Current Post

TWITTER:
{post.twitter_content}

LINKEDIN:
{post.linkedin_content}

## Critique Feedback

{feedback}

## Original Context

{context.to_prompt_section()}

## Instructions

Address the feedback while maintaining authentic voice. Output in same format:

TWITTER:
[revised tweet]

LINKEDIN:
[revised linkedin post]

TONE: [one word]
TOPICS: [comma-separated]
"""
    
    def _parse_response(self, response: str, context: AssembledContext) -> GeneratedPost:
        """Parse LLM response into GeneratedPost."""
        lines = response.strip().split("\n")
        
        twitter_content = ""
        linkedin_content = ""
        tone = "thoughtful"
        topics = []
        
        current_section = None
        linkedin_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            if line_stripped.startswith("TWITTER:"):
                current_section = "twitter"
                twitter_content = line_stripped.replace("TWITTER:", "").strip()
            elif line_stripped.startswith("LINKEDIN:"):
                current_section = "linkedin"
                linkedin_lines = []
            elif line_stripped.startswith("TONE:"):
                current_section = None
                tone = line_stripped.replace("TONE:", "").strip().lower()
            elif line_stripped.startswith("TOPICS:"):
                current_section = None
                topics = [t.strip() for t in line_stripped.replace("TOPICS:", "").split(",")]
            elif current_section == "twitter" and not twitter_content:
                twitter_content = line_stripped
            elif current_section == "linkedin":
                linkedin_lines.append(line)
        
        linkedin_content = "\n".join(linkedin_lines).strip()
        
        return GeneratedPost(
            post_id=GeneratedPost.create_id(context.entry["entry_id"]),
            entry_id=context.entry["entry_id"],
            generated_at=datetime.now().isoformat(),
            twitter_content=twitter_content[:280],  # Enforce limit
            linkedin_content=linkedin_content,
            topics=topics or context.entry.get("connects_to", []),
            tone=tone,
        )
    
    def _generate_fallback(self, context: AssembledContext, error: str) -> GeneratedPost:
        """Generate basic post without LLM (fallback)."""
        entry = context.entry
        
        twitter = entry["summary"]["one_liner"]
        if len(twitter) > 280:
            twitter = twitter[:277] + "..."
        
        linkedin = f"""{entry['summary']['accessible']}

{entry['summary']['technical']}

Significance: {entry['significance']}"""
        
        return GeneratedPost(
            post_id=GeneratedPost.create_id(entry["entry_id"]),
            entry_id=entry["entry_id"],
            generated_at=datetime.now().isoformat(),
            twitter_content=twitter,
            linkedin_content=linkedin,
            topics=entry.get("connects_to", []),
            tone="thoughtful",
        )
