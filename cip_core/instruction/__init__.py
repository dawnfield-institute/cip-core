"""
Unified instruction generation system for CIP operations.

This module provides the InstructionEngine that consolidates and replaces
multiple scattered instruction generators with a unified interface.
"""

from .engine import InstructionEngine

__all__ = [
    "InstructionEngine",
]
