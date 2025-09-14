"""
Unified metadata generation engine.

This module provides the MetadataEngine class that consolidates and replaces
multiple scattered metadata generators with a unified interface.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..engine.repository import RepositoryManager
from ..engine.config import GenerationConfig
from .strategies import MetadataGenerator, RuleBasedGenerator, AIEnhancedGenerator, HybridGenerator


class MetadataEngine:
    """
    Unified system for all metadata generation.
    
    This class consolidates and replaces:
    - DirectoryMetadataGenerator
    - AIEnhancedDirectoryMetadataGenerator
    - Template generation from schemas
    
    Usage:
        engine = MetadataEngine(repo_manager)
        result = engine.generate("ai_enhanced", config)
    """
    
    def __init__(self, repo: RepositoryManager, engine_config=None):
        """
        Initialize metadata engine.
        
        Args:
            repo: Repository manager instance
            engine_config: Optional engine configuration for repository-level settings
        """
        self.repo = repo
        self.engine_config = engine_config
        self.generators: Dict[str, MetadataGenerator] = {
            'rule_based': RuleBasedGenerator(engine_config),
            'ai_enhanced': AIEnhancedGenerator(engine_config),
            'hybrid': HybridGenerator(engine_config)
        }
    
    def generate(self, strategy: str, config: GenerationConfig) -> 'GenerationResult':
        """
        Generate metadata using the specified strategy.
        
        Args:
            strategy: Generation strategy name (rule_based, ai_enhanced, hybrid)
            config: Generation configuration
            
        Returns:
            GenerationResult with success status and generated files
            
        Raises:
            ValueError: If strategy is not available
        """
        if strategy not in self.generators:
            raise ValueError(f"Unknown generation strategy: {strategy}. Available: {list(self.generators.keys())}")
        
        generator = self.generators[strategy]
        return generator.generate(self.repo, config)
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available generation strategies."""
        return list(self.generators.keys())
    
    def register_strategy(self, name: str, generator: MetadataGenerator) -> None:
        """
        Register a custom generation strategy.
        
        Args:
            name: Strategy name
            generator: Generator implementation
        """
        self.generators[name] = generator
    
    def validate_strategy_config(self, strategy: str, config: GenerationConfig) -> List[str]:
        """
        Validate configuration for a specific strategy.
        
        Args:
            strategy: Strategy to validate
            config: Configuration to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if strategy not in self.generators:
            errors.append(f"Unknown strategy: {strategy}")
            return errors
        
        # Strategy-specific validation
        if strategy == "ai_enhanced":
            if not config.ai_provider or config.ai_provider == "none":
                errors.append("AI enhanced strategy requires an AI provider")
            
            if config.ai_provider == "ollama" and not config.ai_model:
                errors.append("Ollama provider requires a model specification")
        
        elif strategy == "hybrid":
            if config.ai_provider and config.ai_provider != "none":
                # Validate AI config for hybrid mode
                if config.ai_provider == "ollama" and not config.ai_model:
                    errors.append("Hybrid strategy with Ollama requires a model specification")
        
        return errors
    
    def get_strategy_info(self, strategy: str) -> Dict[str, Any]:
        """
        Get information about a generation strategy.
        
        Args:
            strategy: Strategy name
            
        Returns:
            Dictionary with strategy information
        """
        if strategy not in self.generators:
            return {"error": f"Unknown strategy: {strategy}"}
        
        generator = self.generators[strategy]
        
        info = {
            "name": strategy,
            "strategy_name": generator.get_strategy_name(),
            "description": self._get_strategy_description(strategy),
            "requirements": self._get_strategy_requirements(strategy)
        }
        
        return info
    
    def _get_strategy_description(self, strategy: str) -> str:
        """Get description for a strategy."""
        descriptions = {
            "rule_based": "Template-based generation using directory analysis and predefined rules. Fast and consistent.",
            "ai_enhanced": "AI-powered generation with intelligent descriptions and semantic analysis. Requires AI provider.",
            "hybrid": "Combines rule-based consistency with AI enhancement. Uses rules as foundation, AI for improvements."
        }
        return descriptions.get(strategy, "Custom strategy")
    
    def _get_strategy_requirements(self, strategy: str) -> Dict[str, Any]:
        """Get requirements for a strategy."""
        requirements = {
            "rule_based": {
                "ai_provider": False,
                "internet": False,
                "dependencies": []
            },
            "ai_enhanced": {
                "ai_provider": True,
                "internet": True,  # Most AI providers require internet
                "dependencies": ["AI provider configuration"]
            },
            "hybrid": {
                "ai_provider": "optional",
                "internet": "optional",
                "dependencies": ["AI provider for enhancement (optional)"]
            }
        }
        return requirements.get(strategy, {})
    
    def generate_preview(self, strategy: str, config: GenerationConfig, path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generate a preview of metadata without writing files.
        
        Args:
            strategy: Generation strategy
            config: Generation configuration
            path: Optional specific path to preview (defaults to repo root)
            
        Returns:
            Preview of metadata that would be generated
        """
        if strategy not in self.generators:
            return {"error": f"Unknown strategy: {strategy}"}
        
        generator = self.generators[strategy]
        target_path = path or self.repo.root_path
        
        try:
            if hasattr(generator, '_generate_directory_metadata'):
                # For backwards compatibility with strategy implementations
                preview_metadata = generator._generate_directory_metadata(self.repo, target_path)
            else:
                # For custom generators, we'd need a preview method
                preview_metadata = {"error": "Preview not available for this strategy"}
            
            return {
                "strategy": strategy,
                "path": str(target_path),
                "metadata": preview_metadata,
                "files_that_would_be_created": [str(target_path / "meta.yaml")]
            }
            
        except Exception as e:
            return {"error": f"Preview generation failed: {str(e)}"}
    
    def cleanup_metadata(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up outdated or invalid metadata files.
        
        Args:
            dry_run: If True, return what would be cleaned without doing it
            
        Returns:
            Summary of cleanup actions
        """
        all_meta_files = self.repo.get_all_metadata_files()
        
        files_to_remove = []
        files_with_issues = []
        
        for meta_file in all_meta_files:
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    import yaml
                    metadata = yaml.safe_load(f)
                
                # Check for issues
                issues = []
                
                # Check schema version
                if 'schema_version' not in metadata:
                    issues.append("Missing schema_version")
                elif metadata['schema_version'] not in ['1.0', '2.0']:
                    issues.append(f"Unsupported schema version: {metadata['schema_version']}")
                
                # Check for empty or generic descriptions
                if 'description' in metadata:
                    desc = metadata['description'].lower()
                    if any(phrase in desc for phrase in ['auto-generated', 'placeholder', 'todo']):
                        issues.append("Generic description")
                
                # Check if directory still exists
                meta_dir = meta_file.parent
                if not meta_dir.exists() or self.repo.is_ignored(meta_dir):
                    files_to_remove.append(str(meta_file))
                
                if issues:
                    files_with_issues.append({
                        "file": str(meta_file),
                        "issues": issues
                    })
                    
            except Exception as e:
                files_with_issues.append({
                    "file": str(meta_file),
                    "issues": [f"Parse error: {str(e)}"]
                })
        
        result = {
            "total_files_checked": len(all_meta_files),
            "files_to_remove": files_to_remove,
            "files_with_issues": files_with_issues,
            "dry_run": dry_run
        }
        
        # Actually remove files if not dry run
        if not dry_run:
            removed_count = 0
            for file_path in files_to_remove:
                try:
                    Path(file_path).unlink()
                    removed_count += 1
                except Exception as e:
                    result[f"removal_error_{file_path}"] = str(e)
            
            result["files_actually_removed"] = removed_count
        
        return result
