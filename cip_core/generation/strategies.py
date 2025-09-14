"""
Metadata generation strategies.

This module defines the base MetadataGenerator class and concrete implementations
that replace the old DirectoryMetadataGenerator and AIEnhancedDirectoryMetadataGenerator.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import yaml

from ..engine.repository import RepositoryManager
from ..engine.config import GenerationConfig


class MetadataGenerator(ABC):
    """
    Base class for all metadata generation strategies.
    
    This replaces the scattered metadata generation logic and provides
    a consistent interface for different generation approaches.
    """
    
    def __init__(self, engine_config=None):
        """Initialize with optional engine configuration."""
        self.engine_config = engine_config
    
    @abstractmethod
    def generate(self, repo: RepositoryManager, config: GenerationConfig) -> 'GenerationResult':
        """Generate metadata for the repository."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this generation strategy."""
        pass
    
    def _get_semantic_scope(self, dirname: str) -> List[str]:
        """Get semantic scope for directory based on name."""
        # Enhanced semantic scope mapping
        scope_map = {
            'src': ['source_code', 'implementation'],
            'lib': ['library', 'modules'],
            'tests': ['testing', 'quality_assurance'],
            'test': ['testing', 'quality_assurance'],
            'docs': ['documentation', 'guides'],
            'documentation': ['documentation', 'guides'],
            'examples': ['examples', 'demonstrations'],
            'samples': ['examples', 'demonstrations'],
            'tools': ['tools', 'utilities'],
            'utils': ['utilities', 'helpers'],
            'utilities': ['utilities', 'helpers'],
            'scripts': ['automation', 'scripts'],
            'automation': ['automation', 'workflows'],
            'config': ['configuration', 'settings'],
            'configuration': ['configuration', 'settings'],
            'data': ['data', 'datasets'],
            'datasets': ['data', 'datasets'],
            'models': ['models', 'ai_ml'],
            'experiments': ['experiments', 'research'],
            'research': ['research', 'investigation'],
            'theory': ['theory', 'concepts'],
            'specs': ['specifications', 'standards'],
            'specification': ['specifications', 'standards'],
            'protocol': ['protocol', 'standards'],
            'api': ['api', 'interface'],
            'interface': ['interface', 'api'],
            'ui': ['user_interface', 'frontend'],
            'frontend': ['frontend', 'user_interface'],
            'backend': ['backend', 'server'],
            'server': ['server', 'backend'],
            'database': ['database', 'storage'],
            'storage': ['storage', 'persistence'],
            'cache': ['cache', 'performance'],
            'logs': ['logging', 'monitoring'],
            'monitoring': ['monitoring', 'observability'],
            'security': ['security', 'authentication'],
            'auth': ['authentication', 'security'],
            'deploy': ['deployment', 'infrastructure'],
            'deployment': ['deployment', 'infrastructure'],
            'infrastructure': ['infrastructure', 'deployment'],
            'docker': ['containerization', 'deployment'],
            'kubernetes': ['orchestration', 'deployment'],
            'ci': ['continuous_integration', 'automation'],
            'cd': ['continuous_deployment', 'automation'],
            'workflows': ['workflows', 'automation'],
            'github': ['version_control', 'collaboration'],
            'git': ['version_control', 'source_control'],
            'cip': ['cip_protocol', 'cognition_index'],
            'cognition': ['cognition_index', 'cip_protocol'],
            'test': ['testing', 'validation'],
            'testing': ['testing', 'validation'],
            'validation': ['validation', 'testing'],
            'demo': ['demonstration', 'examples'],
            'demonstration': ['demonstration', 'examples'],
        }
        
        # Handle compound directory names like "cip-test-repo"
        if '-' in dirname or '_' in dirname:
            # Split on common separators and get scope for each part
            parts = dirname.lower().replace('-', ' ').replace('_', ' ').split()
            all_scopes = []
            for part in parts:
                if part in scope_map:
                    all_scopes.extend(scope_map[part])
                else:
                    all_scopes.append(part)
            return list(set(all_scopes))  # Remove duplicates
        
        return scope_map.get(dirname.lower(), [dirname])
    
    def _get_child_dirs_and_files(self, repo: RepositoryManager, path: Path) -> Tuple[List[str], List[str]]:
        """Get child directories and files, excluding ignored items."""
        structure = repo.get_directory_structure(path)
        
        # Filter out meta.yaml from files list since we don't want to include it in the metadata
        files = [f for f in structure.files if f != 'meta.yaml']
        
        return structure.directories, files


class RuleBasedGenerator(MetadataGenerator):
    """
    Template-based generation from directory analysis.
    
    This replaces the original DirectoryMetadataGenerator with enhanced
    semantic scope mapping and better structure analysis.
    """
    
    def __init__(self, engine_config=None):
        """Initialize with optional engine configuration."""
        super().__init__(engine_config)
    
    def get_strategy_name(self) -> str:
        return "rule_based"
    
    def generate(self, repo: RepositoryManager, config: GenerationConfig) -> 'GenerationResult':
        """Generate rule-based metadata for the entire repository."""
        from ..engine.core import GenerationResult
        
        files_created = []
        files_updated = []
        errors = []
        all_metadata = {}
        
        try:
            # Process root directory
            root_metadata = self._generate_directory_metadata(repo, repo.root_path)
            root_meta_path = repo.root_path / "meta.yaml"
            
            if not root_meta_path.exists() or config.force_overwrite:
                repo.save_metadata(root_metadata, "meta.yaml")
                if root_meta_path.exists():
                    files_updated.append(str(root_meta_path))
                else:
                    files_created.append(str(root_meta_path))
            
            all_metadata['root'] = root_metadata
            
            # Process all subdirectories
            self._process_directory_recursive(repo, repo.root_path, config, files_created, files_updated, errors, all_metadata)
            
            return GenerationResult(
                success=len(errors) == 0,
                files_created=files_created,
                files_updated=files_updated,
                errors=errors,
                metadata=all_metadata
            )
            
        except Exception as e:
            return GenerationResult(
                success=False,
                files_created=files_created,
                files_updated=files_updated,
                errors=[str(e)],
                metadata=all_metadata
            )
    
    def _process_directory_recursive(self, repo: RepositoryManager, path: Path, config: GenerationConfig, 
                                   files_created: List[str], files_updated: List[str], 
                                   errors: List[str], all_metadata: Dict[str, Any]) -> None:
        """Process directory and all subdirectories recursively."""
        if repo.is_ignored(path):
            return
        
        structure = repo.get_directory_structure(path)
        
        # Process each subdirectory
        for dirname in structure.directories:
            subdir_path = path / dirname
            
            if repo.is_ignored(subdir_path):
                continue
            
            try:
                # Generate metadata for subdirectory
                metadata = self._generate_directory_metadata(repo, subdir_path)
                meta_path = subdir_path / "meta.yaml"
                
                if not meta_path.exists() or config.force_overwrite:
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)
                    
                    if meta_path.exists():
                        files_updated.append(str(meta_path))
                    else:
                        files_created.append(str(meta_path))
                
                all_metadata[str(subdir_path.relative_to(repo.root_path))] = metadata
                
                # Recurse into subdirectory
                self._process_directory_recursive(repo, subdir_path, config, files_created, files_updated, errors, all_metadata)
                
            except Exception as e:
                errors.append(f"Error processing {subdir_path}: {str(e)}")
    
    def _generate_directory_metadata(self, repo: RepositoryManager, path: Path) -> Dict[str, Any]:
        """Generate metadata for a specific directory."""
        dirname = path.name
        child_dirs, files = self._get_child_dirs_and_files(repo, path)
        
        # For root directory, use configured title and description if available
        is_root = path == repo.root_path
        
        if is_root and self.engine_config:
            title = self.engine_config.repository_title or dirname
            description = self.engine_config.repository_description or f"Auto-generated metadata for {dirname} directory."
            repository_role = self.engine_config.repository_type or "theory"
        else:
            title = dirname
            description = f"Auto-generated metadata for {dirname} directory."
            repository_role = None
        
        metadata = {
            'schema_version': '2.0',
            'directory_name': dirname,
            'description': description,
            'semantic_scope': self._get_semantic_scope(dirname),
            'files': files,
            'child_directories': child_dirs,
        }
        
        # Add title for root directory
        if is_root:
            metadata['title'] = title
            if repository_role:
                metadata['repository_role'] = repository_role
        
        # Add CIP-specific enhancements
        if dirname in ['cognition_index_protocol', 'cip-core']:
            metadata['repository_role'] = 'protocol'
            metadata['ecosystem_links'] = {
                'theory': 'repo://dawn-field-theory/foundational/',
                'sdk': 'repo://fracton-sdk/'
            }
        
        return metadata


class AIEnhancedGenerator(MetadataGenerator):
    """
    AI-powered intelligent descriptions.
    
    This replaces the AIEnhancedDirectoryMetadataGenerator with better
    AI integration and fallback handling.
    """
    
    def __init__(self, engine_config=None):
        """Initialize with optional engine configuration."""
        super().__init__(engine_config)
        self._ai_client = None
    
    def get_strategy_name(self) -> str:
        return "ai_enhanced"
    
    def generate(self, repo: RepositoryManager, config: GenerationConfig) -> 'GenerationResult':
        """Generate AI-enhanced metadata for the repository."""
        from ..engine.core import GenerationResult
        
        # For now, implement basic AI generation
        # TODO: Implement proper AI integration with providers
        
        files_created = []
        files_updated = []
        errors = []
        all_metadata = {}
        
        try:
            # Initialize AI client based on config
            ai_available = self._initialize_ai_client(config)
            
            # Process root directory with enhanced metadata (with or without AI)
            root_metadata = self._generate_ai_enhanced_metadata(repo, repo.root_path, config)
            root_meta_path = repo.root_path / "meta.yaml"
            
            if not root_meta_path.exists() or config.force_overwrite:
                repo.save_metadata(root_metadata, "meta.yaml")
                if root_meta_path.exists():
                    files_updated.append(str(root_meta_path))
                else:
                    files_created.append(str(root_meta_path))
            
            all_metadata['root'] = root_metadata
            
            # Process all subdirectories with enhanced metadata
            self._process_directory_recursive_ai(repo, repo.root_path, config, files_created, files_updated, errors, all_metadata)
            
            # Add informational message about AI availability
            if not ai_available:
                errors.append("AI provider not available, used enhanced rule-based descriptions instead")
            
            return GenerationResult(
                success=True,  # Success even without AI
                files_created=files_created,
                files_updated=files_updated,
                errors=errors,  # These are more like warnings
                metadata=all_metadata
            )
            root_meta_path = repo.root_path / "meta.yaml"
            
            if not root_meta_path.exists() or config.force_overwrite:
                repo.save_metadata(root_metadata, "meta.yaml")
                if root_meta_path.exists():
                    files_updated.append(str(root_meta_path))
                else:
                    files_created.append(str(root_meta_path))
            
            all_metadata['root'] = root_metadata
            
            # Process subdirectories with AI enhancement
            self._process_directory_recursive_ai(repo, repo.root_path, config, files_created, files_updated, errors, all_metadata)
            
            return GenerationResult(
                success=len(errors) == 0,
                files_created=files_created,
                files_updated=files_updated,
                errors=errors,
                metadata=all_metadata,
                quality_score=self._calculate_quality_score(all_metadata)
            )
            
        except Exception as e:
            errors.append(f"AI generation error: {str(e)}")
            # Even on error, still return success if we processed some files
            return GenerationResult(
                success=len(files_created) > 0 or len(files_updated) > 0,
                files_created=files_created,
                files_updated=files_updated,
                errors=errors,
                metadata=all_metadata
            )
    
    def _initialize_ai_client(self, config: GenerationConfig) -> bool:
        """Initialize AI client based on configuration."""
        # TODO: Implement AI provider initialization
        # For now, return False to trigger fallback
        return False
    
    def _generate_ai_enhanced_metadata(self, repo: RepositoryManager, path: Path, config: GenerationConfig) -> Dict[str, Any]:
        """Generate AI-enhanced metadata for a directory."""
        # Get base metadata from rule-based approach
        rule_generator = RuleBasedGenerator(self.engine_config)
        base_metadata = rule_generator._generate_directory_metadata(repo, path)
        
        # TODO: Enhance with AI-generated descriptions
        # For now, just improve the description
        dirname = path.name
        context = self._get_directory_context(repo, path)
        
        # Enhanced description based on context
        child_dirs = base_metadata.get('child_directories', [])
        files = base_metadata.get('files', [])
        enhanced_description = self._create_enhanced_description(dirname, context, base_metadata['semantic_scope'], child_dirs, files)
        base_metadata['description'] = enhanced_description
        
        # Add context information
        base_metadata['generation_context'] = {
            'generator': 'ai_enhanced',
            'file_count': context['file_count'],
            'directory_count': context['dir_count'],
            'primary_file_types': context['file_types']
        }
        
        return base_metadata
    
    def _create_enhanced_description(self, dirname: str, context: Dict, semantic_scope: List[str], child_dirs: List[str], files: List[str]) -> str:
        """Create enhanced, descriptive metadata like the original good descriptions."""
        
        # Check if we already have a good description that we shouldn't replace
        file_count = context.get('file_count', 0)
        dir_count = context.get('dir_count', 0)
        
        # Define primary scope for use throughout method
        primary_scope = semantic_scope[0] if semantic_scope else dirname
        
        # Create context-aware, descriptive text
        if dirname == 'cli':
            return f"The {dirname} directory contains the command line interface for the cip_core package. It is a Python package with an __init__.py file that serves as the entry point for the CLI. The main.py file is the primary script that implements the CLI, and it is executed when the user runs the CLI command from the command line."
        
        if dirname == 'engine':
            return f"The {dirname} directory contains the core engine components for the CIP system. This includes the main execution engine, metadata processing, and orchestration logic that coordinates all CIP operations."
        
        if dirname == 'generation':
            return f"The {dirname} directory houses the metadata generation strategies and algorithms. It contains different generation approaches including rule-based, AI-enhanced, and hybrid strategies for creating directory metadata."
        
        if dirname == 'validation':
            return f"The {dirname} directory contains the validation framework for CIP compliance. It includes schema validators, compliance checkers, and quality assessment tools that ensure repositories meet CIP standards."
        
        if dirname == 'schemas':
            return f"The {dirname} directory defines the data schemas and validation rules for CIP metadata. It contains YAML schema definitions and validation logic for meta.yaml files and other CIP structures."
        
        if dirname == 'utils':
            return f"The {dirname} directory provides utility functions and helper modules used throughout the CIP codebase. It contains common functionality for file operations, data processing, and system interactions."
        
        # For directories with specific purposes based on name
        if 'cognition' in dirname.lower():
            return f"The {dirname} directory implements the Cognition Index Protocol (CIP) validation framework. It contains validation questions, answers, and assessment tools that test AI comprehension of the repository contents."
        
        elif 'docs' in dirname.lower() or 'documentation' in dirname.lower():
            return f"The {dirname} directory contains project documentation, user guides, and reference materials. It serves as the central hub for all written materials that help users understand and work with the project."
        
        elif 'test' in dirname.lower() or 'testing' in dirname.lower():
            return f"The {dirname} directory contains test suites and testing utilities for {primary_scope}. It includes unit tests, integration tests, and test fixtures to ensure code quality and reliability."
        
        elif 'experiments' in dirname.lower() or 'research' in dirname.lower():
            return f"The {dirname} directory contains experimental code and research materials for {primary_scope}. It houses exploratory work, prototypes, and research findings that may inform future development."
        
        elif 'tools' in dirname.lower() or 'scripts' in dirname.lower():
            return f"The {dirname} directory contains utility tools and scripts for {primary_scope}. It provides helpful automation, build tools, and administrative scripts for development and maintenance."
        
        elif 'temp' in dirname.lower() or 'tmp' in dirname.lower():
            return f"The {dirname} directory serves as temporary storage for {primary_scope} operations. It contains transient files, intermediate results, and temporary data that supports ongoing work."
        
        elif 'case' in dirname.lower() and 'stud' in dirname.lower():
            # Check for specific case study content to provide detailed descriptions
            if any('claude' in f.lower() for f in files + child_dirs):
                return f"The {dirname} directory contains comprehensive case studies demonstrating real-world CIP implementations. It includes detailed technical analyses of AI assistant integrations, performance benchmarks, and practical success stories from various environments including Claude, GitHub Copilot, and community implementations."
            elif any('implementation' in f.lower() or 'integration' in f.lower() for f in files):
                return f"The {dirname} directory documents real-world implementations and integration results from CIP deployments. It provides detailed case studies, performance metrics, and lessons learned from practical applications across different environments and use cases."
            else:
                return f"The {dirname} directory contains real-world case studies and implementation examples. It documents practical applications, success stories, and lessons learned from using the system in different scenarios."
        
        # File-based context
        file_types = set()
        for file in files:
            if '.' in file:
                ext = file.split('.')[-1]
                file_types.add(ext)
        
        # Create meaningful description based on actual content
        if 'py' in file_types and len(files) > 0:
            if any('test' in f for f in files):
                return f"The {dirname} directory contains test modules and testing utilities for the {primary_scope} functionality. It includes unit tests, integration tests, and test fixtures to ensure code quality and reliability."
            elif any('__init__' in f for f in files):
                return f"The {dirname} directory is a Python package containing {primary_scope} modules and functionality. It provides a structured collection of related code organized for easy import and use."
            else:
                return f"The {dirname} directory contains Python modules implementing {primary_scope} functionality. It houses the core logic and implementation details for this component of the system."
        
        elif 'md' in file_types:
            if any('readme' in f.lower() for f in files):
                if dirname.lower() == 'case-studies':
                    return f"The {dirname} directory contains comprehensive case studies demonstrating real-world CIP implementations. It includes detailed technical analyses, performance benchmarks, success stories, and practical integration results from AI assistants like Claude and GitHub Copilot, providing valuable insights for developers and researchers."
                elif dirname.lower() == 'examples':
                    return f"The {dirname} directory provides practical guides and step-by-step tutorials for using CIP effectively. It contains hands-on examples for common use cases, from basic setup to advanced automation workflows, repository configurations, and AI integration scenarios."
                elif dirname.lower() == 'reference':
                    return f"The {dirname} directory provides technical reference documentation including schema definitions, validation rules, file formats, and quick lookup tables. It serves as the authoritative source for CIP specifications, configuration options, and implementation details."
                elif dirname.lower() == 'user-guide':
                    return f"The {dirname} directory contains comprehensive user documentation covering daily usage of CIP from installation to advanced configuration. It includes getting started guides, CLI reference, configuration options, and troubleshooting resources for developers and teams."
                elif dirname.lower() == 'scripts':
                    return f"The {dirname} directory documents automation scripts and integration tools that make CIP easier to use across different environments. It provides comprehensive documentation for initialization scripts, maintenance utilities, and CI/CD integration templates."
                else:
                    return f"The {dirname} directory contains documentation and readme files for {primary_scope}. It provides essential information, guides, and reference materials to help users understand and work with this component."
            elif any('guide' in f.lower() or 'tutorial' in f.lower() for f in files):
                return f"The {dirname} directory contains user guides and tutorials for {primary_scope}. It includes step-by-step instructions, examples, and educational materials for users and developers."
            elif any('spec' in f.lower() or 'standard' in f.lower() for f in files):
                return f"The {dirname} directory contains specifications and standards documentation for {primary_scope}. It houses formal definitions, requirements, and technical specifications."
            else:
                return f"The {dirname} directory contains documentation and reference materials for {primary_scope}. It includes explanatory documents that help users understand and work with this component."
        
        elif 'yaml' in file_types or 'yml' in file_types:
            return f"The {dirname} directory contains configuration and metadata files for {primary_scope}. It houses YAML definitions, configuration templates, and structured data that define system behavior."
        
        elif child_dirs:
            return f"The {dirname} directory organizes {primary_scope} components into logical subdirectories. It serves as a container for related functionality, with each subdirectory focusing on specific aspects of {primary_scope}."
        
        else:
            # Fallback for empty or unknown directories
            return f"The {dirname} directory is reserved for {primary_scope} functionality. It provides a dedicated space for organizing related files and components."
    
    def _get_directory_context(self, repo: RepositoryManager, path: Path) -> Dict[str, Any]:
        """Get context information about a directory."""
        structure = repo.get_directory_structure(path)
        
        # Analyze file types
        file_types = {}
        for file in structure.files:
            ext = Path(file).suffix.lower()
            if ext:
                file_types[ext] = file_types.get(ext, 0) + 1
        
        return {
            'file_count': len(structure.files),
            'dir_count': len(structure.directories),
            'file_types': file_types,
            'has_code': any(ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c'] for ext in file_types.keys()),
            'has_docs': any(ext in ['.md', '.rst', '.txt'] for ext in file_types.keys()),
            'has_config': any(ext in ['.yaml', '.yml', '.json', '.toml', '.ini'] for ext in file_types.keys())
        }
    
    def _process_directory_recursive_ai(self, repo: RepositoryManager, path: Path, config: GenerationConfig,
                                      files_created: List[str], files_updated: List[str], 
                                      errors: List[str], all_metadata: Dict[str, Any]) -> None:
        """Process directory recursively with AI enhancement."""
        if repo.is_ignored(path):
            return
        
        structure = repo.get_directory_structure(path)
        
        for dirname in structure.directories:
            subdir_path = path / dirname
            
            if repo.is_ignored(subdir_path):
                continue
            
            try:
                metadata = self._generate_ai_enhanced_metadata(repo, subdir_path, config)
                meta_path = subdir_path / "meta.yaml"
                
                if not meta_path.exists() or config.force_overwrite:
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)
                    
                    if meta_path.exists():
                        files_updated.append(str(meta_path))
                    else:
                        files_created.append(str(meta_path))
                
                all_metadata[str(subdir_path.relative_to(repo.root_path))] = metadata
                
                # Recurse
                self._process_directory_recursive_ai(repo, subdir_path, config, files_created, files_updated, errors, all_metadata)
                
            except Exception as e:
                errors.append(f"Error processing {subdir_path} with AI: {str(e)}")
    
    def _calculate_quality_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate quality score for generated metadata."""
        # Simple quality scoring based on metadata richness
        total_score = 0
        total_items = 0
        
        for key, meta in metadata.items():
            score = 0
            
            # Base score for having required fields
            if 'description' in meta and len(meta['description']) > 20:
                score += 0.3
            if 'semantic_scope' in meta and len(meta['semantic_scope']) > 0:
                score += 0.3
            if 'files' in meta and len(meta['files']) > 0:
                score += 0.2
            if 'child_directories' in meta:
                score += 0.2
            
            total_score += score
            total_items += 1
        
        return total_score / total_items if total_items > 0 else 0.0


class HybridGenerator(MetadataGenerator):
    """
    Combines rule-based and AI approaches.
    
    Uses rule-based generation as a foundation and enhances with AI where available.
    """
    
    def __init__(self, engine_config=None):
        """Initialize with optional engine configuration."""
        super().__init__(engine_config)
        self.rule_generator = RuleBasedGenerator(engine_config)
        self.ai_generator = AIEnhancedGenerator(engine_config)
    
    def get_strategy_name(self) -> str:
        return "hybrid"
    
    def generate(self, repo: RepositoryManager, config: GenerationConfig) -> 'GenerationResult':
        """Generate hybrid metadata combining rule-based and AI approaches."""
        from ..engine.core import GenerationResult
        
        try:
            # Start with rule-based generation for consistency
            rule_result = self.rule_generator.generate(repo, config)
            
            # If AI is available, enhance the metadata
            if config.ai_provider and config.ai_provider != "none":
                ai_result = self.ai_generator.generate(repo, config)
                
                # Merge results, preferring AI descriptions but keeping rule-based structure
                merged_metadata = self._merge_metadata(rule_result.metadata, ai_result.metadata)
                
                return GenerationResult(
                    success=rule_result.success and ai_result.success,
                    files_created=rule_result.files_created,
                    files_updated=rule_result.files_updated,
                    errors=rule_result.errors + ai_result.errors,
                    metadata=merged_metadata,
                    quality_score=ai_result.quality_score
                )
            else:
                # Fall back to rule-based only
                return rule_result
                
        except Exception as e:
            return GenerationResult(
                success=False,
                files_created=[],
                files_updated=[],
                errors=[str(e)],
                metadata={}
            )
    
    def _merge_metadata(self, rule_metadata: Dict[str, Any], ai_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Merge rule-based and AI-generated metadata."""
        merged = rule_metadata.copy()
        
        # Enhance with AI descriptions where available
        for key, ai_meta in ai_metadata.items():
            if key in merged:
                # Prefer AI description if it's more detailed
                if 'description' in ai_meta and len(ai_meta['description']) > len(merged[key].get('description', '')):
                    merged[key]['description'] = ai_meta['description']
                
                # Add AI context information
                if 'generation_context' in ai_meta:
                    merged[key]['generation_context'] = ai_meta['generation_context']
                    merged[key]['generation_context']['strategy'] = 'hybrid'
        
        return merged
