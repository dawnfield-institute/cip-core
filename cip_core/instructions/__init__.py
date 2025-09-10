"""
CIP Instructions Generation System

Automatically generates AI-readable instructions and guidance files for 
repository navigation, understanding, and interaction following the
Cognition Index Protocol specifications.
"""

from .generator import CIPInstructionsGenerator, InstructionTemplate, generate_cip_instructions

__all__ = [
    'CIPInstructionsGenerator',
    'InstructionTemplate', 
    'generate_cip_instructions'
]
