"""
Core engine module for CIP operations.

This module provides the unified interface for all CIP functionality,
replacing scattered automation and coordination classes.
"""

from .core import CIPEngine
from .repository import RepositoryManager, ProjectType
from .config import CIPConfig, GenerationConfig, ValidationRules, AIProviderConfig

__all__ = [
    "CIPEngine",
    "RepositoryManager",
    "ProjectType",
    "CIPConfig",
    "GenerationConfig", 
    "ValidationRules",
    "AIProviderConfig",
]
