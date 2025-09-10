"""
CIP VM Service Integration for AI-powered repository analysis.

This module enables triggering heavy computational tasks on a dedicated VM
with Ollama, GPU acceleration, and comprehensive AI analysis capabilities.
"""

from .service import (
    VMServiceConfig,
    AnalysisJob,
    CIPVMService,
    GitHubVMIntegration,
    load_vm_config
)

__all__ = [
    'VMServiceConfig',
    'AnalysisJob', 
    'CIPVMService',
    'GitHubVMIntegration',
    'load_vm_config'
]
