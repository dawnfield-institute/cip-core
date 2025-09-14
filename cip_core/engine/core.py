"""
Core CIP engine - central coordinator for all CIP operations.

This module provides the main CIPEngine class that serves as the unified
interface for all CIP functionality, replacing scattered automation classes.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from .config import CIPConfig, GenerationConfig, ValidationRules
from .repository import RepositoryManager, ProjectType


@dataclass
class InitConfig:
    """Configuration for repository initialization."""
    project_type: ProjectType
    title: Optional[str] = None
    description: Optional[str] = None
    license: Optional[str] = None
    force: bool = False
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None


@dataclass
class GenerationResult:
    """Result of metadata generation operation."""
    success: bool
    files_created: List[str]
    files_updated: List[str]
    errors: List[str]
    metadata: Dict[str, Any]
    quality_score: Optional[float] = None


@dataclass
class ValidationResult:
    """Result of validation operation."""
    success: bool
    score: float
    total_checks: int
    passed_checks: int
    issues: List[Dict[str, Any]]
    summary: str


@dataclass
class InstructionResult:
    """Result of instruction generation operation."""
    success: bool
    instructions_file: str
    content: str
    errors: List[str]


class CIPEngine:
    """
    Central coordinator for all CIP operations.
    
    This class serves as the main entry point for all CIP functionality,
    replacing the scattered CIPAutomation and related classes.
    
    Usage:
        engine = CIPEngine("/path/to/repo")
        result = engine.generate_metadata("ai_enhanced")
        validation = engine.validate_repository()
    """
    
    def __init__(self, repo_path: str, config: Optional[CIPConfig] = None):
        """
        Initialize CIP engine for a repository.
        
        Args:
            repo_path: Path to the repository root
            config: Optional configuration. If None, will load from .cip/core.yaml
        """
        self.repo = RepositoryManager(repo_path)
        
        # Load configuration
        if config is None:
            config_path = self.repo.cip_directory / "core.yaml"
            self.config = CIPConfig.load_from_file(str(config_path))
        else:
            self.config = config
        
        # Initialize sub-engines (lazy loading)
        self._metadata_engine = None
        self._validation_engine = None
        self._instruction_engine = None
    
    @property
    def metadata(self):
        """Get metadata engine (lazy loaded)."""
        if self._metadata_engine is None:
            # Import here to avoid circular imports
            from ..generation import MetadataEngine
            self._metadata_engine = MetadataEngine(self.repo, self.config)
        return self._metadata_engine
    
    @property
    def validation(self):
        """Get validation engine (lazy loaded).""" 
        if self._validation_engine is None:
            # Import here to avoid circular imports
            from ..validation import ValidationEngine
            self._validation_engine = ValidationEngine(self.repo)
        return self._validation_engine
    
    @property
    def instructions(self):
        """Get instruction engine (lazy loaded)."""
        if self._instruction_engine is None:
            # Import here to avoid circular imports
            from ..instruction import InstructionEngine
            self._instruction_engine = InstructionEngine(self.repo)
        return self._instruction_engine
    
    def initialize_repository(self, config: InitConfig) -> InitConfig:
        """
        Initialize repository with CIP structure and metadata.
        
        Args:
            config: Initialization configuration
            
        Returns:
            InitResult with success status and created files
        """
        try:
            # Ensure CIP structure exists
            self.repo.ensure_cip_structure()
            
            # Detect project type if not specified
            if config.project_type is None:
                config.project_type = self.repo.detect_project_type()
            
            # Update engine config
            self.config.repository_type = config.project_type.value
            self.config.repository_title = config.title
            self.config.repository_description = config.description
            
            # Set AI provider if specified
            if config.ai_provider:
                self.config.ai_integration.provider = config.ai_provider
                self.config.generation.ai_provider = config.ai_provider
                
            if config.ai_model:
                self.config.ai_integration.model = config.ai_model
                self.config.generation.ai_model = config.ai_model
            
            # Save configuration
            config_path = self.repo.cip_directory / "core.yaml"
            self.config.save_to_file(str(config_path))
            
            # Generate initial metadata
            generation_config = GenerationConfig(
                strategy="ai_enhanced" if config.ai_provider else "rule_based",
                force_overwrite=config.force
            )
            
            metadata_result = self.generate_metadata("rule_based", generation_config)
            
            # Generate instructions
            instruction_result = self.generate_instructions()
            
            return InitResult(
                success=True,
                files_created=[
                    str(config_path),
                    *metadata_result.files_created,
                    instruction_result.instructions_file if instruction_result.success else ""
                ],
                project_type=config.project_type,
                errors=metadata_result.errors + instruction_result.errors
            )
            
        except Exception as e:
            return InitResult(
                success=False,
                files_created=[],
                project_type=config.project_type,
                errors=[str(e)]
            )
    
    def generate_metadata(self, strategy: str = None, config: Optional[GenerationConfig] = None) -> GenerationResult:
        """
        Generate metadata using specified strategy.
        
        Args:
            strategy: Generation strategy (rule_based, ai_enhanced, hybrid)
            config: Optional generation configuration
            
        Returns:
            GenerationResult with success status and generated files
        """
        # Use config from engine if not provided
        if config is None:
            config = self.config.generation
        
        # Use strategy from config if not provided
        if strategy is None:
            strategy = self.config.generation.strategy
        
        try:
            return self.metadata.generate(strategy, config)
        except Exception as e:
            return GenerationResult(
                success=False,
                files_created=[],
                files_updated=[],
                errors=[str(e)],
                metadata={}
            )
    
    def validate_repository(self, rules: Optional[ValidationRules] = None) -> ValidationResult:
        """
        Validate repository for CIP compliance.
        
        Args:
            rules: Optional validation rules. Uses engine config if not provided.
            
        Returns:
            ValidationResult with compliance score and issues
        """
        # Use config from engine if not provided
        if rules is None:
            rules = self.config.validation
        
        try:
            return self.validation.validate(rules)
        except Exception as e:
            return ValidationResult(
                success=False,
                score=0.0,
                total_checks=0,
                passed_checks=0,
                issues=[{"message": str(e), "severity": "error"}],
                summary=f"Validation failed: {str(e)}"
            )
    
    def generate_instructions(self, template: Optional[str] = None) -> InstructionResult:
        """
        Generate AI instruction files.
        
        Args:
            template: Optional instruction template name
            
        Returns:
            InstructionResult with generated instructions
        """
        try:
            return self.instructions.generate_instructions(template)
        except Exception as e:
            return InstructionResult(
                success=False,
                instructions_file="",
                content="",
                errors=[str(e)]
            )
    
    def get_repository_status(self) -> Dict[str, Any]:
        """Get comprehensive repository status."""
        return {
            "path": str(self.repo.path),
            "has_cip_setup": self.repo.has_cip_setup,
            "project_type": self.repo.detect_project_type().value,
            "metadata_files": len(self.repo.get_all_metadata_files()),
            "config": {
                "cip_version": self.config.cip_version,
                "schema_version": self.config.schema_version,
                "ai_provider": self.config.ai_integration.provider,
                "validation_rules": self.config.validation.enabled_rules
            }
        }
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update engine configuration."""
        # Update configuration based on provided updates
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Save updated configuration
        config_path = self.repo.cip_directory / "core.yaml"
        self.config.save_to_file(str(config_path))


# Backwards compatibility alias
@dataclass
class InitResult(InitConfig):
    """Result of repository initialization."""
    success: bool = False
    files_created: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.files_created is None:
            self.files_created = []
        if self.errors is None:
            self.errors = []
