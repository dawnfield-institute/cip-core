"""
AI-enhanced directory metadata generator using Ollama for intelligent 
semantic scope and description generation.
"""

import os
import yaml
import fnmatch
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..utils import YamlParser


class AIEnhancedDirectoryMetadataGenerator:
    """
    AI-enhanced directory metadata generator using Ollama for intelligent 
    semantic scope and description generation.
    """
    
    def __init__(self, repo_root: str, model: str = "codellama:latest"):
        self.repo_root = Path(repo_root)
        self.model = model
        self.gitignore_patterns = self._load_gitignore_patterns()
        self.yaml_parser = YamlParser()
        
        # Try to import Ollama integration
        try:
            from ..ollama_local import OllamaClient, AIMetadataEnhancer
            self.ollama = OllamaClient()  # Use default base URL
            self.ai_enhancer = AIMetadataEnhancer(model=model)
            self.ai_enabled = True
            print(f"✅ AI enhancement enabled with model: {model}")
        except ImportError:
            print("⚠️  Ollama not available, falling back to rule-based generation")
            self.ai_enabled = False
    
    def _load_gitignore_patterns(self) -> List[str]:
        """Load and parse .gitignore patterns."""
        gitignore_path = self.repo_root / '.gitignore'
        patterns = []
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def _is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored based on gitignore patterns."""
        rel_path = str(path.relative_to(self.repo_root))
        
        for pattern in self.gitignore_patterns:
            if pattern.endswith('/'):
                dir_pattern = pattern[:-1]
                if fnmatch.fnmatch(rel_path, dir_pattern) or fnmatch.fnmatch(path.name, dir_pattern):
                    return True
                parts = rel_path.split(os.sep)
                for part in parts:
                    if fnmatch.fnmatch(part, dir_pattern):
                        return True
            else:
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
                    return True
                parts = rel_path.split(os.sep)
                for part in parts:
                    if fnmatch.fnmatch(part, pattern):
                        return True
        
        return False
    
    def _get_directory_context(self, path: Path) -> Dict[str, Any]:
        """Gather comprehensive context about directory for AI analysis."""
        context = {
            'directory_name': path.name,
            'full_path': str(path.relative_to(self.repo_root)),
            'files': [],
            'subdirectories': [],
            'file_types': set(),
            'notable_files': [],
            'file_contents': {},
            'readme_content': None,
            'total_size': 0
        }
        
        # Analyze directory contents
        if path.exists():
            for entry in path.iterdir():
                if entry.name.startswith('.') and entry.name != '.gitignore':
                    continue
                if self._is_ignored(entry):
                    continue
                
                if entry.is_file():
                    context['files'].append(entry.name)
                    if entry.suffix:
                        context['file_types'].add(entry.suffix.lower())
                    
                    # Flag notable files and read their content
                    if entry.name.lower() in ['readme.md', '__init__.py', 'setup.py', 'requirements.txt', 'main.py']:
                        context['notable_files'].append(entry.name)
                    
                    # Read content of key files for analysis
                    if self._should_read_file_content(entry):
                        try:
                            content = self._read_file_safely(entry)
                            if content:
                                context['file_contents'][entry.name] = content
                                if entry.name.lower().startswith('readme'):
                                    context['readme_content'] = content
                        except Exception as e:
                            print(f"⚠️  Could not read {entry.name}: {e}")
                    
                    # Track file size
                    try:
                        context['total_size'] += entry.stat().st_size
                    except:
                        pass
                        
                elif entry.is_dir():
                    context['subdirectories'].append(entry.name)
        
        context['file_types'] = list(context['file_types'])
        return context
    
    def _should_read_file_content(self, file_path: Path) -> bool:
        """Determine if we should read file content for AI analysis."""
        # File size limit (100KB)
        try:
            if file_path.stat().st_size > 100 * 1024:
                return False
        except:
            return False
        
        # Read these file types
        read_extensions = {'.md', '.txt', '.py', '.yaml', '.yml', '.json', '.toml', '.cfg', '.ini'}
        
        # Read these specific files
        read_filenames = {
            'readme.md', 'readme.txt', 'readme', 'changelog.md', 'contributing.md',
            'license', 'license.txt', 'authors', 'contributors.md', 'setup.py',
            'requirements.txt', 'pyproject.toml', 'package.json', '__init__.py'
        }
        
        return (file_path.suffix.lower() in read_extensions or 
                file_path.name.lower() in read_filenames)
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read file content with encoding detection."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Limit content length for AI processing
                return content[:2000] if len(content) > 2000 else content
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    return content[:2000] if len(content) > 2000 else content
            except:
                return None
        except Exception:
            return None
    
    def _generate_ai_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to generate intelligent metadata with file content analysis."""
        if not self.ai_enabled:
            return self._fallback_metadata(context)
        
        # Determine directory type and schema
        directory_schema = self._get_directory_schema(context)
        enhanced_context = self._build_enhanced_context(context)
        
        prompt = f"""
You are analyzing a directory in a software project repository to generate accurate metadata.

DIRECTORY ANALYSIS:
Name: {context['directory_name']}
Path: {context.get('full_path', context['directory_name'])}
Files: {context['files']}
File Types: {context['file_types']}
Notable Files: {context['notable_files']}
Subdirectories: {context.get('subdirectories', [])}
Total Size: {context.get('total_size', 0)} bytes

ACTUAL FILE CONTENTS:
{self._format_file_contents(context.get('file_contents', {}))}

DIRECTORY TYPE: {directory_schema['type']}
REQUIRED COVERAGE: {directory_schema['coverage_areas']}

DOMAIN CONTEXT:
{enhanced_context}

CRITICAL INSTRUCTIONS:
- Focus on the FUNCTIONAL PURPOSE of this directory - what it does, not what files it contains
- IGNORE meta.yaml files - do not describe metadata structures or configuration files
- Write DEFINITIVE descriptions - no "appears", "likely", "seems", or "probably"
- Use PRESENT TENSE and ACTIVE VOICE
- Be SPECIFIC about the business/technical purpose and functionality
- Cover the required areas: {', '.join(directory_schema['coverage_areas'])}
- Base analysis on ACTUAL implementation code, not metadata files
- Do NOT describe the directory as "a Python package" or mention __init__.py files
- Focus on WHAT THE CODE DOES, not how it's packaged

EXAMPLE GOOD DESCRIPTIONS:
- "Handles Ollama AI integration for enhanced metadata generation and semantic analysis"
- "Implements repository navigation and cross-project content resolution using repo:// URLs"
- "Provides VM service integration for cloud-based AI processing and analysis jobs"
- "Manages automated workflow generation for GitHub Actions and CI/CD pipelines"

EXAMPLE BAD PHRASES TO AVOID:
- "Python package" → describe the functionality instead
- "contains meta.yaml" → ignore metadata files completely
- "appears to contain" → "provides" or "implements"
- "directory structure" → focus on purpose instead

Based on the actual implementation code and functionality, provide:

DESCRIPTION: [2-3 definitive sentences explaining the specific technical purpose and functionality this directory provides]
SEMANTIC_SCOPE: [4-6 precise, technical keywords that accurately categorize the functionality, not the file structure]

Format as:
DESCRIPTION: [description]
SEMANTIC_SCOPE: [keyword1, keyword2, keyword3, keyword4]
"""
        
        try:
            response = self.ollama.generate(self.model, prompt)
            return self._parse_ai_response(response, context)
        except Exception as e:
            print(f"⚠️  AI generation failed for {context['directory_name']}: {e}")
            return self._fallback_metadata(context)
    
    def _get_directory_schema(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically determine directory type based on content patterns."""
        path = context.get('full_path', '').lower()
        files = [f.lower() for f in context.get('files', [])]
        file_types = context.get('file_types', [])
        file_contents = context.get('file_contents', {})
        
        # Analyze content to determine type
        content_text = ' '.join(file_contents.values()).lower()
        
        # Code/implementation detection
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'}
        if (any(ext in file_types for ext in code_extensions) or 
            '__init__.py' in files or 'setup.py' in files or 'package.json' in files):
            return {
                'type': 'code_module',
                'coverage_areas': ['functionality', 'key_classes_functions', 'dependencies', 'usage_patterns']
            }
        
        # Documentation detection
        doc_indicators = ['readme', 'documentation', 'guide', 'tutorial', 'manual']
        if (any(indicator in path for indicator in doc_indicators) or
            any(indicator in ' '.join(files) for indicator in doc_indicators) or
            len([f for f in files if f.endswith('.md')]) > 1):
            return {
                'type': 'documentation',
                'coverage_areas': ['content_overview', 'target_audience', 'key_topics', 'usage_instructions']
            }
        
        # Test/testing detection
        test_indicators = ['test', 'spec', 'unittest']
        if any(indicator in path for indicator in test_indicators):
            return {
                'type': 'testing',
                'coverage_areas': ['test_scope', 'test_methods', 'coverage_areas', 'execution_requirements']
            }
        
        # Configuration detection
        config_files = {'.yaml', '.yml', '.json', '.toml', '.cfg', '.ini', '.conf'}
        if (any(ext in file_types for ext in config_files) or
            any(config_word in ' '.join(files) for config_word in ['config', 'settings', 'env'])):
            return {
                'type': 'configuration',
                'coverage_areas': ['configuration_purpose', 'parameter_definitions', 'usage_context', 'dependencies']
            }
        
        # Build/deployment detection
        build_indicators = ['build', 'deploy', 'ci', 'cd', 'pipeline', 'workflow', 'docker']
        if any(indicator in path for indicator in build_indicators):
            return {
                'type': 'build_deployment',
                'coverage_areas': ['build_process', 'deployment_steps', 'environment_requirements', 'automation_tools']
            }
        
        # Default general type
        return {
            'type': 'general',
            'coverage_areas': ['content_overview', 'purpose', 'key_components', 'relationships']
        }
    
    def _format_file_contents(self, file_contents: Dict[str, str]) -> str:
        """Format file contents for AI analysis, excluding metadata files."""
        if not file_contents:
            return "No readable file contents available."
        
        # Filter out metadata and configuration files to focus on implementation
        excluded_files = {'meta.yaml', 'map.yaml', '__pycache__', '.gitignore', 'requirements.txt', 'setup.py'}
        
        formatted = []
        for filename, content in file_contents.items():
            # Skip metadata files that don't represent functionality
            if filename in excluded_files or filename.endswith('.pyc'):
                continue
                
            # Extract key information from content
            lines = content.split('\n')
            preview = '\n'.join(lines[:10])  # First 10 lines
            
            formatted.append(f"=== {filename} ===")
            formatted.append(preview)
        
        if not formatted:
            return "Only metadata files present - focus on directory name and structure for analysis."
            if len(lines) > 10:
                formatted.append(f"... ({len(lines)} total lines)")
            formatted.append("")
        
        return '\n'.join(formatted)
    
    def _build_enhanced_context(self, context: Dict[str, Any]) -> str:
        """Build enhanced context clues for better AI understanding."""
        clues = []
        
        # Analyze file patterns for domain-specific hints
        files = context.get('files', [])
        file_text = ' '.join(files).lower()
        
        # Common technology patterns
        tech_patterns = {
            'ai_ml': ['ai', 'ml', 'neural', 'model', 'inference', 'training', 'dataset'],
            'web': ['html', 'css', 'js', 'react', 'vue', 'angular', 'api', 'rest'],
            'data': ['data', 'sql', 'database', 'analytics', 'pipeline', 'etl'],
            'devops': ['docker', 'kubernetes', 'ci', 'cd', 'pipeline', 'deploy'],
            'testing': ['test', 'spec', 'unit', 'integration', 'e2e', 'mock'],
            'config': ['config', 'settings', 'env', 'properties', 'conf']
        }
        
        detected_domains = []
        for domain, keywords in tech_patterns.items():
            if any(keyword in file_text for keyword in keywords):
                detected_domains.append(domain.replace('_', '/'))
        
        if detected_domains:
            clues.append(f"Technology domains: {', '.join(detected_domains)}")
        
        # Documentation patterns
        doc_patterns = ['readme', 'guide', 'tutorial', 'manual', 'doc', 'howto']
        if any(pattern in file_text for pattern in doc_patterns):
            clues.append("Contains documentation or instructional materials")
        
        # Code patterns
        code_indicators = ['main', 'init', 'setup', 'lib', 'util', 'helper', 'core']
        if any(indicator in file_text for indicator in code_indicators):
            clues.append("Contains implementation or utility code")
        
        # File type analysis
        file_types = context.get('file_types', [])
        type_descriptions = {
            '.md': "Markdown documentation",
            '.py': "Python code",
            '.js': "JavaScript code", 
            '.ts': "TypeScript code",
            '.yaml': "YAML configuration",
            '.yml': "YAML configuration",
            '.json': "JSON data/config",
            '.toml': "TOML configuration",
            '.sql': "SQL database files",
            '.sh': "Shell scripts",
            '.dockerfile': "Docker containers"
        }
        
        for file_type in file_types:
            if file_type in type_descriptions:
                clues.append(type_descriptions[file_type] + " present")
        
        # Content-based analysis from actual file reading
        file_contents = context.get('file_contents', {})
        if file_contents:
            content_text = ' '.join(file_contents.values()).lower()
            
            # Look for specific keywords in content
            if 'class ' in content_text or 'def ' in content_text:
                clues.append("Contains class or function definitions")
            if 'import ' in content_text:
                clues.append("Contains import statements indicating dependencies")
            if 'test' in content_text and 'assert' in content_text:
                clues.append("Contains test cases with assertions")
            if '# ' in content_text or '## ' in content_text:
                clues.append("Contains structured documentation with headers")
        
        return '\n'.join(f"- {clue}" for clue in clues) if clues else "- No specific domain patterns detected"
    
    def _parse_ai_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured metadata."""
        lines = response.strip().split('\n')
        description = context['directory_name']  # fallback
        semantic_scope = [context['directory_name']]  # fallback
        
        for line in lines:
            line = line.strip()
            if line.startswith('DESCRIPTION:'):
                description = line.replace('DESCRIPTION:', '').strip()
                # Clean up quotes and formatting
                description = description.strip('"\'')
            elif line.startswith('SEMANTIC_SCOPE:'):
                scope_text = line.replace('SEMANTIC_SCOPE:', '').strip()
                
                # Handle different formats: [item1, item2] or item1, item2
                scope_text = scope_text.strip('[]')
                scope_text = scope_text.replace('"', '').replace("'", '')
                
                # Parse comma-separated values and clean them
                semantic_scope = [s.strip().lower() for s in scope_text.split(',') if s.strip()]
                if not semantic_scope:
                    semantic_scope = [context['directory_name']]
        
        return {
            'description': description,
            'semantic_scope': semantic_scope
        }
    
    def _fallback_metadata(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate metadata using rule-based fallback."""
        dirname = context['directory_name']
        
        # Rule-based semantic scope mapping
        scope_map = {
            'automation': ['automation', 'tools', 'workflows'],
            'cli': ['cli', 'command-line', 'interface'],
            'instructions': ['instructions', 'documentation', 'ai-guidance'],
            'navigation': ['navigation', 'routing', 'discovery'],
            'ollama_local': ['ollama', 'ai', 'local-models'],
            'schemas': ['schemas', 'validation', 'structure'],
            'utils': ['utilities', 'helpers', 'tools'],
            'validators': ['validation', 'compliance', 'checking'],
            'vm': ['virtual-machine', 'cloud', 'analysis'],
            'tests': ['testing', 'validation', 'qa'],
            'templates': ['templates', 'scaffolding', 'generators'],
            '__pycache__': ['cache', 'python', 'compiled'],
            'egg-info': ['packaging', 'metadata', 'distribution'],
        }
        
        semantic_scope = scope_map.get(dirname.lower(), [dirname])
        
        # Generate description based on context
        if '__init__.py' in context['notable_files']:
            description = f"Python package containing {dirname} functionality and modules."
        elif '.py' in context['file_types']:
            description = f"Python module directory for {dirname} implementation."
        elif '.md' in context['file_types']:
            description = f"Documentation directory containing {dirname} related content."
        elif context['subdirectories']:
            description = f"Container directory organizing {dirname} related subdirectories."
        else:
            description = f"Directory containing {dirname} related files and resources."
        
        return {
            'description': description,
            'semantic_scope': semantic_scope
        }
    
    def generate_directory_metadata(self, path: Path) -> Dict[str, Any]:
        """Generate AI-enhanced metadata for a specific directory."""
        context = self._get_directory_context(path)
        files, child_dirs = self._get_child_dirs_and_files(path)
        
        # Get AI-generated content
        if self.ai_enabled:
            try:
                ai_metadata = self.ai_enhancer.enhance_metadata(path)
                description = ai_metadata.get('description', self._generate_fallback_description(context))
                semantic_scope = ai_metadata.get('semantic_scope', [path.name])
            except Exception as e:
                print(f"⚠️  AI generation failed, using fallback: {e}")
                fallback = self._generate_fallback_metadata(context, path.name)
                description = fallback['description']
                semantic_scope = fallback['semantic_scope']
        else:
            fallback = self._generate_fallback_metadata(context, path.name)
            description = fallback['description']
            semantic_scope = fallback['semantic_scope']
        
        metadata = {
            'schema_version': '2.0',
            'directory_name': path.name,
            'description': description,
            'semantic_scope': semantic_scope,
            'files': files,
            'child_directories': child_dirs,
        }
        
        # Add CIP-specific enhancements
        if path.name in ['cognition_index_protocol', 'cip-core']:
            metadata['repository_role'] = 'protocol'
            metadata['ecosystem_links'] = {
                'theory': 'repo://dawn-field-theory/foundational/',
                'sdk': 'repo://fracton-sdk/'
            }
        
        return metadata
    
    def _get_child_dirs_and_files(self, path: Path) -> tuple[List[str], List[str]]:
        """Get child directories and files, excluding ignored items."""
        files = []
        child_dirs = []
        
        if not path.exists():
            return files, child_dirs
            
        for entry in sorted(path.iterdir()):
            if entry.name.startswith('.') and entry.name != '.gitignore':
                continue
            if self._is_ignored(entry):
                continue
                
            if entry.is_dir():
                child_dirs.append(entry.name)
            elif entry.name != 'meta.yaml':
                files.append(entry.name)
        
        return files, child_dirs
    
    def process_directory(self, path: Path, force: bool = False):
        """Process directory and all subdirectories recursively."""
        if self._is_ignored(path):
            return
        
        meta_path = path / 'meta.yaml'
        
        # Generate meta.yaml if it doesn't exist or force is True
        if not meta_path.exists() or force:
            print(f"🤖 Generating AI-enhanced metadata for {path.name}...")
            metadata = self.generate_directory_metadata(path)
            with open(meta_path, 'w', encoding='utf-8') as f:
                yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)
            print(f"✅ Generated meta.yaml at {meta_path}")
        
        # Recurse into subdirectories
        for entry in path.iterdir():
            if entry.name.startswith('.') and entry.name != '.gitignore':
                continue
            if entry.is_dir() and not self._is_ignored(entry):
                self.process_directory(entry, force)
    
    def process_repository(self, force: bool = False):
        """Process entire repository starting from root."""
        print(f"🚀 Processing repository with AI enhancement: {self.repo_root}")
        print(f"🤖 AI Model: {self.model}")
        print(f"📋 Loaded {len(self.gitignore_patterns)} gitignore patterns")
        self.process_directory(self.repo_root, force)
    
    def _generate_fallback_description(self, context: Dict[str, Any]) -> str:
        """Generate fallback description when AI is not available."""
        dir_name = context.get('directory_name', 'unknown')
        file_count = context.get('file_count', 0)
        
        # Basic rule-based description
        if file_count == 0:
            return f"Empty directory: {dir_name}"
        elif any(f.endswith('.py') for f in context.get('files', [])):
            return f"Python module containing {file_count} files"
        elif any(f.endswith('.md') for f in context.get('files', [])):
            return f"Documentation directory with {file_count} files"
        else:
            return f"Directory containing {file_count} files"
    
    def _generate_fallback_metadata(self, context: Dict[str, Any], dir_name: str) -> Dict[str, Any]:
        """Generate fallback metadata when AI is not available."""
        return {
            'description': self._generate_fallback_description(context),
            'semantic_scope': [dir_name]
        }
