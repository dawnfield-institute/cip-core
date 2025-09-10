"""
CIP-C# Core modules
from .schemas import MetaYamlSchema, FilenameTagSchema, RepositorySchema
from .validators import ComplianceValidator, MetadataValidator, CrossRepoValidator
from .placeholders import ComprehensionBenchmark, QuestionGenerator
from .navigation import RepositoryResolver, DependencyGraph, CrossRepoValidator
from .automation import CIPAutomation, DirectoryMetadataGenerator, GitHubWorkflowGenerator
from .vm import CIPVMService, GitHubVMIntegration, load_vm_config

# Convenience imports for common workflows
from .workflows import validate_repository, score_comprehension, resolve_contentition Index Protocol Implementation

A Python library for validating, scoring, and navigating repositories
following the Cognition Index Protocol (CIP) specification.
"""

__version__ = "0.1.0-dev"
__author__ = "Peter Groom, Dawn Field Institute"

# Core modules
from .schemas import MetaYamlSchema, FilenameTagSchema, RepositorySchema
from .validators import ComplianceValidator, MetadataValidator, CrossRepoValidator
from .placeholders import ComprehensionBenchmark, QuestionGenerator
from .navigation import RepositoryResolver, DependencyGraph, ContentDiscovery
from .automation import CIPAutomation, DirectoryMetadataGenerator, GitHubWorkflowGenerator

# Convenience imports for common workflows
from .workflows import validate_repository, score_comprehension, resolve_content

__all__ = [
    # Core classes
    "MetaYamlSchema",
    "FilenameTagSchema", 
    "RepositorySchema",
    "ComplianceValidator",
    "MetadataValidator",
    "CrossRepoValidator",
    "ComprehensionBenchmark",
    "QuestionGenerator",
    "RepositoryResolver",
    "DependencyGraph",
    
    # Automation classes
    "CIPAutomation",
    "DirectoryMetadataGenerator",
    "GitHubWorkflowGenerator",
    
    # VM Service classes
    "CIPVMService",
    "GitHubVMIntegration",
    "load_vm_config",
    
    # Workflow functions
    "validate_repository",
    "score_comprehension", 
    "resolve_content",
]
