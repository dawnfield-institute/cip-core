"""
Multi-repository navigation and content resolution.

Implements the repo:// URL scheme and cross-repository
content discovery as designed in the CIP specification.
"""

from .resolver import (
    RepositoryResolver, 
    RepositoryReference, 
    ResolvedContent,
    DependencyGraph,
    ContentDiscovery
)

__all__ = [
    'RepositoryResolver',
    'RepositoryReference', 
    'ResolvedContent',
    'DependencyGraph',
    'ContentDiscovery'
]
