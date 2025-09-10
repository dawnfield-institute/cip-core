"""
Local Ollama integration for AI-powered metadata generation.
"""

from .client import (
    OllamaClient,
    AIMetadataEnhancer,
    test_ollama_integration
)

__all__ = [
    'OllamaClient',
    'AIMetadataEnhancer', 
    'test_ollama_integration'
]
