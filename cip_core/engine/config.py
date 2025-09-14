"""
Configuration management for CIP engine.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml


@dataclass
class GenerationConfig:
    """Configuration for metadata generation."""
    strategy: str = "rule_based"  # rule_based, ai_enhanced, hybrid
    force_overwrite: bool = False
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    custom_prompts_dir: Optional[str] = None
    quality_threshold: float = 0.7


@dataclass
class ValidationRules:
    """Configuration for validation rules."""
    enabled_rules: List[str] = field(default_factory=lambda: ["schema", "compliance"])
    quality_threshold: float = 0.7
    strict_mode: bool = False
    auto_fix: bool = False
    
    def should_run(self, validator_name: str) -> bool:
        """Check if a validator should be run."""
        return validator_name in self.enabled_rules


@dataclass
class AIProviderConfig:
    """Configuration for AI providers."""
    provider: str = "none"  # none, ollama, openai, anthropic
    model: str = "llama2"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30


@dataclass
class CIPConfig:
    """
    Central configuration for CIP operations.
    Consolidates configuration from multiple sources.
    """
    cip_version: str = "4.0"
    schema_version: str = "2.0"
    
    # Generation settings
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    
    # Validation settings  
    validation: ValidationRules = field(default_factory=ValidationRules)
    
    # AI integration settings
    ai_integration: AIProviderConfig = field(default_factory=AIProviderConfig)
    
    # Repository settings
    repository_type: Optional[str] = None
    repository_title: Optional[str] = None
    repository_description: Optional[str] = None
    
    @classmethod
    def load_from_file(cls, path: str) -> 'CIPConfig':
        """Load configuration from a YAML file."""
        file_path = Path(path)
        if not file_path.exists():
            # Return default config if file doesn't exist
            return cls()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        # Handle nested configurations
        config = cls()
        
        # Update top-level fields
        for key, value in data.items():
            if key in ['cip_version', 'schema_version', 'repository_type', 
                      'repository_title', 'repository_description']:
                setattr(config, key, value)
        
        # Update generation config
        if 'generation' in data:
            gen_data = data['generation']
            config.generation = GenerationConfig(
                strategy=gen_data.get('strategy', 'rule_based'),
                force_overwrite=gen_data.get('force_overwrite', False),
                ai_provider=gen_data.get('ai_provider'),
                ai_model=gen_data.get('ai_model'),
                custom_prompts_dir=gen_data.get('custom_prompts_dir'),
                quality_threshold=gen_data.get('quality_threshold', 0.7)
            )
        
        # Update validation config
        if 'validation' in data:
            val_data = data['validation']
            config.validation = ValidationRules(
                enabled_rules=val_data.get('enabled_rules', ['schema', 'compliance']),
                quality_threshold=val_data.get('quality_threshold', 0.7),
                strict_mode=val_data.get('strict_mode', False),
                auto_fix=val_data.get('auto_fix', False)
            )
        
        # Update AI config
        if 'ai_integration' in data:
            ai_data = data['ai_integration']
            config.ai_integration = AIProviderConfig(
                provider=ai_data.get('provider', 'none'),
                model=ai_data.get('model', 'llama2'),
                api_key=ai_data.get('api_key'),
                base_url=ai_data.get('base_url'),
                timeout=ai_data.get('timeout', 30)
            )
        
        return config
    
    def save_to_file(self, path: str) -> None:
        """Save configuration to a YAML file."""
        data = {
            'cip_version': self.cip_version,
            'schema_version': self.schema_version,
            'generation': {
                'strategy': self.generation.strategy,
                'force_overwrite': self.generation.force_overwrite,
                'ai_provider': self.generation.ai_provider,
                'ai_model': self.generation.ai_model,
                'custom_prompts_dir': self.generation.custom_prompts_dir,
                'quality_threshold': self.generation.quality_threshold,
            },
            'validation': {
                'enabled_rules': self.validation.enabled_rules,
                'quality_threshold': self.validation.quality_threshold,
                'strict_mode': self.validation.strict_mode,
                'auto_fix': self.validation.auto_fix,
            },
            'ai_integration': {
                'provider': self.ai_integration.provider,
                'model': self.ai_integration.model,
                'api_key': self.ai_integration.api_key,
                'base_url': self.ai_integration.base_url,
                'timeout': self.ai_integration.timeout,
            }
        }
        
        # Add repository info if available
        if self.repository_type:
            data['repository_type'] = self.repository_type
        if self.repository_title:
            data['repository_title'] = self.repository_title
        if self.repository_description:
            data['repository_description'] = self.repository_description
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    
    def merge_with(self, other: 'CIPConfig') -> 'CIPConfig':
        """Merge this config with another, with other taking precedence."""
        # Create a new config with values from other where they exist
        merged = CIPConfig()
        
        # Merge simple fields
        merged.cip_version = other.cip_version or self.cip_version
        merged.schema_version = other.schema_version or self.schema_version
        merged.repository_type = other.repository_type or self.repository_type
        merged.repository_title = other.repository_title or self.repository_title
        merged.repository_description = other.repository_description or self.repository_description
        
        # Merge generation config
        merged.generation = GenerationConfig(
            strategy=other.generation.strategy if other.generation.strategy != "rule_based" else self.generation.strategy,
            force_overwrite=other.generation.force_overwrite or self.generation.force_overwrite,
            ai_provider=other.generation.ai_provider or self.generation.ai_provider,
            ai_model=other.generation.ai_model or self.generation.ai_model,
            custom_prompts_dir=other.generation.custom_prompts_dir or self.generation.custom_prompts_dir,
            quality_threshold=other.generation.quality_threshold if other.generation.quality_threshold != 0.7 else self.generation.quality_threshold
        )
        
        # Merge validation config
        merged.validation = ValidationRules(
            enabled_rules=other.validation.enabled_rules if other.validation.enabled_rules != ["schema", "compliance"] else self.validation.enabled_rules,
            quality_threshold=other.validation.quality_threshold if other.validation.quality_threshold != 0.7 else self.validation.quality_threshold,
            strict_mode=other.validation.strict_mode or self.validation.strict_mode,
            auto_fix=other.validation.auto_fix or self.validation.auto_fix
        )
        
        # Merge AI config
        merged.ai_integration = AIProviderConfig(
            provider=other.ai_integration.provider if other.ai_integration.provider != "none" else self.ai_integration.provider,
            model=other.ai_integration.model if other.ai_integration.model != "llama2" else self.ai_integration.model,
            api_key=other.ai_integration.api_key or self.ai_integration.api_key,
            base_url=other.ai_integration.base_url or self.ai_integration.base_url,
            timeout=other.ai_integration.timeout if other.ai_integration.timeout != 30 else self.ai_integration.timeout
        )
        
        return merged
