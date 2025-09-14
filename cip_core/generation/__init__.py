"""
Unified metadata generation system.

This module provides the MetadataEngine that consolidates and replaces:
- DirectoryMetadataGenerator
- AIEnhancedDirectoryMetadataGenerator  
- Template generation from schemas
"""

from .engine import MetadataEngine
from .strategies import (
    MetadataGenerator,
    RuleBasedGenerator,
    AIEnhancedGenerator,
    HybridGenerator
)

__all__ = [
    "MetadataEngine",
    "MetadataGenerator",
    "RuleBasedGenerator", 
    "AIEnhancedGenerator",
    "HybridGenerator",
]
