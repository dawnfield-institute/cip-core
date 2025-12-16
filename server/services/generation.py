"""Generation Service - AI-powered content generation."""

import os
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import yaml

logger = logging.getLogger(__name__)


@dataclass
class GeneratedContent:
    """Generated content with metadata."""
    content: str
    format: str  # "yaml", "markdown", "text"
    confidence: float = 0.0
    suggestions: list[str] = field(default_factory=list)
    model_used: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0


class GenerationService:
    """
    Service for AI-powered content generation.
    
    Uses LLM (Anthropic Claude or Ollama) to generate meta.yaml, README, summaries.
    """
    
    def __init__(self, llm_config=None):
        """Initialize with LLM configuration."""
        self.llm_config = llm_config
        
        # Handle both Pydantic models and dicts
        if llm_config is None:
            self.provider = "anthropic"
            self.model = "claude-sonnet-4-20250514"
            self.base_url = "http://localhost:11434"
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        elif hasattr(llm_config, 'provider'):  # Pydantic model
            self.provider = llm_config.provider
            self.model = llm_config.model
            self.base_url = getattr(llm_config, 'base_url', 'http://localhost:11434')
            self.api_key = getattr(llm_config, 'api_key', None) or os.getenv("ANTHROPIC_API_KEY")
        else:  # Dict
            self.provider = llm_config.get("provider", "anthropic")
            self.model = llm_config.get("model", "claude-sonnet-4-20250514")
            self.base_url = llm_config.get("base_url", "http://localhost:11434")
            self.api_key = llm_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        
        self.llm_client = None
        logger.info(f"GenerationService initialized: provider={self.provider}, model={self.model}")
        
    async def _get_llm(self):
        """Get or initialize LLM client."""
        if self.llm_client is None:
            if self.provider == "anthropic":
                try:
                    from anthropic import AsyncAnthropic
                    self.llm_client = AsyncAnthropic(api_key=self.api_key)
                    logger.info("Anthropic client initialized")
                except ImportError:
                    logger.error("anthropic package not installed. Install: pip install anthropic")
                    raise
            elif self.provider == "ollama":
                try:
                    import httpx
                    self.llm_client = httpx.AsyncClient(base_url=self.base_url)
                    logger.info(f"Ollama client initialized: {self.base_url}")
                except ImportError:
                    logger.error("httpx package not installed")
                    raise
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        return self.llm_client
    
    async def _call_llm(self, prompt: str, system: str = None) -> tuple[str, dict]:
        """
        Call LLM with prompt, return (response_text, metadata).
        
        Handles both Anthropic and Ollama providers.
        """
        client = await self._get_llm()
        
        if self.provider == "anthropic":
            messages = [{"role": "user", "content": prompt}]
            kwargs = {"model": self.model, "messages": messages, "max_tokens": 4096}
            if system:
                kwargs["system"] = system
            
            response = await client.messages.create(**kwargs)
            
            return (
                response.content[0].text,
                {
                    "model": response.model,
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens
                }
            )
        
        elif self.provider == "ollama":
            payload = {
                "model": self.model,
                "prompt": f"{system}\n\n{prompt}" if system else prompt,
                "stream": False
            }
            
            response = await client.post("/api/generate", json=payload)
            data = response.json()
            
            return (
                data.get("response", ""),
                {
                    "model": self.model,
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0)
                }
            )
        
        raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _analyze_directory(self, path: str) -> dict:
        """Analyze directory contents for context."""
        path_obj = Path(path)
        
        if not path_obj.exists():
            return {"error": "Path does not exist"}
        
        # Count files by extension
        file_types = {}
        file_count = 0
        dir_count = 0
        readme_exists = False
        license_exists = False
        
        for item in path_obj.iterdir():
            if item.is_file():
                file_count += 1
                ext = item.suffix or "no_extension"
                file_types[ext] = file_types.get(ext, 0) + 1
                
                if item.name.upper() == "README.MD":
                    readme_exists = True
                elif item.name.upper() == "LICENSE":
                    license_exists = True
            elif item.is_dir() and not item.name.startswith("."):
                dir_count += 1
        
        # Read sample files for context
        sample_content = []
        for pattern in ["*.py", "*.md", "*.yaml", "*.yml"]:
            for file in list(path_obj.glob(pattern))[:3]:  # Max 3 per type
                try:
                    content = file.read_text(encoding="utf-8")
                    if len(content) < 5000:  # Only small files
                        sample_content.append({
                            "name": file.name,
                            "content": content[:1000]  # First 1000 chars
                        })
                except Exception:
                    pass
        
        return {
            "path": str(path_obj),
            "name": path_obj.name,
            "file_count": file_count,
            "dir_count": dir_count,
            "file_types": file_types,
            "readme_exists": readme_exists,
            "license_exists": license_exists,
            "sample_files": sample_content
        }
    
    async def generate_meta(
        self,
        path: str,
        style: str = "minimal"
    ) -> GeneratedContent:
        """
        Generate meta.yaml for a directory.
        
        style: "minimal", "standard", "comprehensive"
        """
        # Analyze directory
        analysis = self._analyze_directory(path)
        
        if "error" in analysis:
            return GeneratedContent(
                content="",
                format="yaml",
                confidence=0.0,
                suggestions=[f"Error: {analysis['error']}"]
            )
        
        # Build prompt based on style
        system_prompt = """You are an expert at creating CIP (Cognition Index Protocol) v2.0 metadata files.
Generate valid meta.yaml content following this schema:

Required fields:
- schema_version: "2.0"
- repository_role: one of [theory, sdk, devkit, models, protocol, infrastructure, ecosystem_coordinator]

Optional fields:
- title: string
- description: string
- version: string
- authors: array of strings
- license: string
- tags: array of strings
- ecosystem_links: object with repo:// URIs
- cognition_metrics: {complexity_score, comprehension_baseline, last_benchmark}

Return ONLY the YAML content, no explanations."""

        user_prompt = f"""Generate a {style} meta.yaml for this directory:

Directory: {analysis['name']}
Files: {analysis['file_count']} files, {analysis['dir_count']} directories
File types: {', '.join(f'{k}({v})' for k, v in list(analysis['file_types'].items())[:5])}
Has README: {analysis['readme_exists']}
Has LICENSE: {analysis['license_exists']}

Sample files:
"""
        
        for sample in analysis['sample_files'][:2]:
            user_prompt += f"\n{sample['name']}:\n{sample['content'][:300]}...\n"
        
        user_prompt += f"\nGenerate a {style} meta.yaml with appropriate repository_role and description."
        
        try:
            response_text, metadata = await self._call_llm(user_prompt, system_prompt)
            
            # Extract YAML from response (remove markdown code blocks if present)
            yaml_content = response_text.strip()
            if yaml_content.startswith("```yaml"):
                yaml_content = yaml_content.split("```yaml")[1].split("```")[0].strip()
            elif yaml_content.startswith("```"):
                yaml_content = yaml_content.split("```")[1].split("```")[0].strip()
            
            # Validate it's proper YAML
            try:
                parsed = yaml.safe_load(yaml_content)
                confidence = 0.9 if "schema_version" in parsed and "repository_role" in parsed else 0.6
            except yaml.YAMLError:
                confidence = 0.3
            
            return GeneratedContent(
                content=yaml_content,
                format="yaml",
                confidence=confidence,
                suggestions=[],
                model_used=metadata.get("model", self.model),
                prompt_tokens=metadata.get("prompt_tokens", 0),
                completion_tokens=metadata.get("completion_tokens", 0)
            )
            
        except Exception as e:
            logger.error(f"Error generating meta.yaml: {e}")
            return GeneratedContent(
                content="",
                format="yaml",
                confidence=0.0,
                suggestions=[f"Error: {str(e)}"]
            )
    
    
    async def generate_readme(
        self,
        path: str,
        include_badges: bool = True,
        include_toc: bool = True
    ) -> GeneratedContent:
        """Generate README.md for a directory."""
        # Analyze directory
        analysis = self._analyze_directory(path)
        
        if "error" in analysis:
            return GeneratedContent(
                content="",
                format="markdown",
                confidence=0.0,
                suggestions=[f"Error: {analysis['error']}"]
            )
        
        # Check if meta.yaml exists for context
        meta_context = ""
        meta_path = Path(path) / "meta.yaml"
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta_data = yaml.safe_load(f)
                meta_context = f"\nExisting meta.yaml:\n{yaml.dump(meta_data)}\n"
            except Exception:
                pass
        
        system_prompt = """You are an expert technical writer creating README.md files for software projects.
Generate clear, professional documentation that explains what the project does and how to use it.

Structure:
1. Title and brief description
2. Badges (if requested)
3. Installation/Setup
4. Usage examples
5. Project structure
6. Contributing/License

Use proper Markdown formatting. Be concise but informative."""

        user_prompt = f"""Generate a README.md for this project:

Directory: {analysis['name']}
Files: {analysis['file_count']} files, {analysis['dir_count']} directories
File types: {', '.join(f'{k}({v})' for k, v in list(analysis['file_types'].items())[:5])}
{meta_context}

Sample files:
"""
        
        for sample in analysis['sample_files'][:3]:
            user_prompt += f"\n{sample['name']}:\n{sample['content'][:400]}...\n"
        
        user_prompt += f"\nGenerate a professional README.md"
        if include_badges:
            user_prompt += " with status badges"
        if include_toc:
            user_prompt += " and table of contents"
        user_prompt += "."
        
        try:
            response_text, metadata = await self._call_llm(user_prompt, system_prompt)
            
            # Clean markdown (remove code block wrappers if present)
            md_content = response_text.strip()
            if md_content.startswith("```markdown"):
                md_content = md_content.split("```markdown")[1].split("```")[0].strip()
            elif md_content.startswith("```md"):
                md_content = md_content.split("```md")[1].split("```")[0].strip()
            elif md_content.startswith("```"):
                md_content = md_content.split("```")[1].split("```")[0].strip()
            
            # Check quality
            has_title = md_content.startswith("#")
            has_sections = md_content.count("##") >= 2
            confidence = 0.85 if (has_title and has_sections) else 0.6
            
            return GeneratedContent(
                content=md_content,
                format="markdown",
                confidence=confidence,
                suggestions=[],
                model_used=metadata.get("model", self.model),
                prompt_tokens=metadata.get("prompt_tokens", 0),
                completion_tokens=metadata.get("completion_tokens", 0)
            )
            
        except Exception as e:
            logger.error(f"Error generating README: {e}")
            return GeneratedContent(
                content="",
                format="markdown",
                confidence=0.0,
                suggestions=[f"Error: {str(e)}"]
            )
    
    
    async def generate_summary(
        self,
        content: str,
        max_length: int = 200
    ) -> str:
        """Generate a summary of content."""
        if len(content) <= max_length:
            return content
        
        system_prompt = f"You are a technical summarizer. Create concise summaries under {max_length} characters."
        user_prompt = f"Summarize this content in {max_length} characters or less:\n\n{content[:2000]}"
        
        try:
            response_text, _ = await self._call_llm(user_prompt, system_prompt)
            return response_text.strip()[:max_length]
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return content[:max_length] + "..."
    
    async def enhance_meta(
        self,
        content: dict
    ) -> tuple[dict, list[str]]:
        """
        Enhance existing meta.yaml with AI suggestions.
        
        Returns (enhanced_content, suggestions)
        """
        current_yaml = yaml.dump(content)
        
        system_prompt = """You are a CIP v2.0 metadata expert. Analyze meta.yaml and suggest improvements.
Return JSON with: {"enhanced": <enhanced_yaml_as_string>, "suggestions": [list of strings]}"""

        user_prompt = f"""Analyze this meta.yaml and suggest improvements:

{current_yaml}

Suggest better:
- Description clarity
- Tag relevance
- Missing optional fields
- Cognition metrics

Return JSON format."""

        try:
            response_text, _ = await self._call_llm(user_prompt, system_prompt)
            
            # Try to parse as JSON
            import json
            data = json.loads(response_text)
            enhanced_yaml = data.get("enhanced", current_yaml)
            suggestions = data.get("suggestions", [])
            
            try:
                enhanced_dict = yaml.safe_load(enhanced_yaml)
                return enhanced_dict, suggestions
            except yaml.YAMLError:
                return content, suggestions
                
        except Exception as e:
            logger.error(f"Error enhancing meta: {e}")
            return content, [f"Error: {str(e)}"]
    
    async def suggest_tags(self, content: str) -> list[str]:
        """Suggest semantic tags for content."""
        system_prompt = "You are a tagging expert. Generate 3-5 relevant semantic tags."
        user_prompt = f"Generate semantic tags for this content:\n\n{content[:1000]}\n\nReturn only comma-separated tags."
        
        try:
            response_text, _ = await self._call_llm(user_prompt, system_prompt)
            tags = [tag.strip() for tag in response_text.split(",")]
            return tags[:5]  # Max 5 tags
        except Exception as e:
            logger.error(f"Error suggesting tags: {e}")
            return []
