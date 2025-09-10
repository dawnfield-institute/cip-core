"""
CIP automation workflows and GitHub Actions integration.
"""

from .ai_enhanced_generator import AIEnhancedDirectoryMetadataGenerator
from .metadata_generator import DirectoryMetadataGenerator
from .github_workflows import GitHubWorkflowGenerator
from .coordinator import CIPAutomation

__all__ = [
    'AIEnhancedDirectoryMetadataGenerator',
    'DirectoryMetadataGenerator', 
    'GitHubWorkflowGenerator',
    'CIPAutomation'
]
