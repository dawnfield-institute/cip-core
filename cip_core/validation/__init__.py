"""
Unified validation system for CIP compliance.

This module provides the ValidationEngine that consolidates and replaces
multiple scattered validators with a unified interface.
"""

from .engine import ValidationEngine

__all__ = [
    "ValidationEngine",
]
