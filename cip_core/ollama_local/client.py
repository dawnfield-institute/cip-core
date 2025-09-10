"""
Local Ollama integration for AI-enhanced CIP metadata generation.

This is a prototype implementation that runs locally, demonstrating
what the VM service would do with AI-powered analysis.
"""

import json
import requests
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

from ..utils import YamlParser


class OllamaClient:
    """Local Ollama client for AI-powered analysis."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def generate(self, model: str, prompt: str, system: str = None) -> str:
        """Generate text using Ollama model."""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        response = self.session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        return response.json()["response"]
    
    def list_models(self) -> List[str]:
        """List available models."""
        response = self.session.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        
        models = response.json().get("models", [])
        return [model["name"] for model in models]


class AIMetadataEnhancer:
    """AI-powered metadata enhancement using Ollama."""
    
    def __init__(self, model: str = "codellama:latest"):
        self.ollama = OllamaClient()
        self.model = model
        self.yaml_parser = YamlParser()
    
    def analyze_directory_content(self, directory_path: Path) -> Dict[str, Any]:
        """Analyze directory content and generate AI insights."""
        
        # Gather directory information
        files = []
        code_files = []
        doc_files = []
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                rel_path = file_path.relative_to(directory_path)
                files.append(str(rel_path))
                
                # Categorize files
                if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                    code_files.append(str(rel_path))
                elif file_path.suffix in ['.md', '.txt', '.rst', '.doc']:
                    doc_files.append(str(rel_path))
        
        # Read some sample content
        sample_content = []
        for file_path in list(directory_path.iterdir())[:5]:  # First 5 files
            if file_path.is_file() and file_path.stat().st_size < 10000:  # Small files only
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        sample_content.append({
                            "file": file_path.name,
                            "content": content[:500]  # First 500 chars
                        })
                except:
                    continue
        
        return {
            "directory_name": directory_path.name,
            "total_files": len(files),
            "code_files": code_files,
            "doc_files": doc_files,
            "sample_content": sample_content
        }
    
    def generate_ai_description(self, analysis: Dict[str, Any]) -> str:
        """Generate AI-powered description for directory."""
        
        system_prompt = """You are an expert code analyst. Generate a concise, technical description 
        of what this directory contains based on the file structure and content samples. 
        Focus on the purpose, functionality, and role within a larger project.
        Keep it under 100 words and professional."""
        
        content_summary = ""
        if analysis["sample_content"]:
            content_summary = "\n".join([
                f"File {item['file']}: {item['content'][:200]}..."
                for item in analysis["sample_content"][:3]
            ])
        
        prompt = f"""
        Analyze this directory structure:
        
        Directory: {analysis['directory_name']}
        Total files: {analysis['total_files']}
        Code files: {analysis['code_files'][:10]}  # First 10
        Documentation: {analysis['doc_files'][:5]}   # First 5
        
        Sample content:
        {content_summary}
        
        Generate a professional description of what this directory contains and its purpose:
        """
        
        try:
            response = self.ollama.generate(self.model, prompt, system_prompt)
            return response.strip()
        except Exception as e:
            print(f"⚠️  AI generation failed: {e}")
            return f"Directory containing {analysis['total_files']} files including code and documentation."
    
    def generate_semantic_tags(self, analysis: Dict[str, Any], description: str) -> List[str]:
        """Generate semantic tags using AI analysis."""
        
        system_prompt = """Generate exactly 3-5 semantic tags that describe the purpose and content of this directory.
        Tags should be lowercase, single words or hyphenated phrases. Focus on functionality, technology, and purpose.
        Return ONLY the tags separated by commas, no other text or formatting."""
        
        prompt = f"""
        Directory: {analysis['directory_name']}
        Description: {description}
        Code files: {analysis['code_files'][:5]}
        
        Generate semantic tags (comma-separated):
        """
        
        try:
            response = self.ollama.generate(self.model, prompt, system_prompt)
            # Clean up the response
            cleaned_response = response.strip().replace('*', '').replace('`', '').replace('\n', ' ')
            tags = [tag.strip().lower() for tag in cleaned_response.split(',')]
            # Filter valid tags
            valid_tags = []
            for tag in tags:
                if tag and len(tag) > 1 and tag.replace('-', '').replace('_', '').isalpha():
                    valid_tags.append(tag)
            return valid_tags[:5]  # Max 5 tags
        except Exception as e:
            print(f"⚠️  Tag generation failed: {e}")
            return [analysis['directory_name'].lower()]
    
    def calculate_complexity_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate complexity score based on directory content."""
        
        score = 0.0
        
        # Base score from file count
        score += min(analysis['total_files'] * 0.1, 1.0)
        
        # Code complexity bonus
        if analysis['code_files']:
            score += len(analysis['code_files']) * 0.05
        
        # Documentation bonus (good complexity management)
        if analysis['doc_files']:
            score += len(analysis['doc_files']) * 0.02
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def enhance_metadata(self, directory_path: Path) -> Dict[str, Any]:
        """Generate AI-enhanced metadata for directory."""
        
        print(f"🤖 Analyzing {directory_path.name} with {self.model}...")
        
        # Analyze directory content
        analysis = self.analyze_directory_content(directory_path)
        
        # Generate AI insights
        ai_description = self.generate_ai_description(analysis)
        semantic_tags = self.generate_semantic_tags(analysis, ai_description)
        complexity_score = self.calculate_complexity_score(analysis)
        
        # Create enhanced metadata
        metadata = {
            "schema_version": "2.0",
            "directory_name": directory_path.name,
            "description": ai_description,
            "semantic_scope": semantic_tags,
            "files": [f for f in os.listdir(directory_path) 
                     if os.path.isfile(os.path.join(directory_path, f)) and f != "meta.yaml"],
            "child_directories": [d for d in os.listdir(directory_path) 
                                if os.path.isdir(os.path.join(directory_path, d))],
            "ai_analysis": {
                "complexity_score": complexity_score,
                "total_files": analysis['total_files'],
                "code_files_count": len(analysis['code_files']),
                "doc_files_count": len(analysis['doc_files']),
                "analyzed_by": f"{self.model}",
                "analysis_version": "1.0"
            }
        }
        
        return metadata
    
    def process_repository(self, repo_path: Path, force: bool = False):
        """Process entire repository with AI-enhanced metadata."""
        
        print(f"🚀 AI-enhanced metadata generation for {repo_path}")
        print(f"🤖 Using model: {self.model}")
        
        # Process directories recursively
        for directory in repo_path.rglob("*"):
            if not directory.is_dir():
                continue
                
            # Skip hidden directories
            if any(part.startswith('.') for part in directory.parts):
                continue
            
            # Skip if meta.yaml exists and not forcing
            meta_path = directory / "meta.yaml"
            if meta_path.exists() and not force:
                print(f"⏭️  Skipping {directory.name} (meta.yaml exists)")
                continue
            
            try:
                # Generate AI-enhanced metadata
                metadata = self.enhance_metadata(directory)
                
                # Write metadata file
                with open(meta_path, 'w', encoding='utf-8') as f:
                    yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)
                
                print(f"✅ Enhanced {meta_path}")
                
            except Exception as e:
                print(f"❌ Failed to process {directory}: {e}")


def test_ollama_integration(repo_path: str = ".", model: str = "codellama:latest"):
    """Test function for AI-enhanced metadata generation."""
    
    enhancer = AIMetadataEnhancer(model)
    repo_path = Path(repo_path)
    
    # Test on a single directory first
    test_dir = None
    for directory in repo_path.iterdir():
        if directory.is_dir() and not directory.name.startswith('.'):
            test_dir = directory
            break
    
    if test_dir:
        print(f"🧪 Testing AI enhancement on: {test_dir.name}")
        metadata = enhancer.enhance_metadata(test_dir)
        
        print("\n📊 Generated Metadata:")
        print(yaml.dump(metadata, sort_keys=False, allow_unicode=True))
        
        return metadata
    else:
        print("❌ No suitable test directory found")
        return None
