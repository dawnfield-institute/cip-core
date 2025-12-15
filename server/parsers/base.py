"""
Abstract Parser Interface

All parsers must implement this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ParsedEntity:
    """An entity extracted from source code."""
    
    type: str  # function, class, method, variable, etc.
    name: str
    content: str  # Full text content
    line_start: int
    line_end: int
    
    # Optional metadata
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parent: Optional[str] = None  # Parent entity name
    children: List[str] = None  # Child entity names
    imports: List[str] = None  # Imported modules
    calls: List[str] = None  # Called functions
    metadata: Dict[str, Any] = None


@dataclass
class ParseResult:
    """Result of parsing a file."""
    
    path: str
    language: str
    entities: List[ParsedEntity]
    imports: List[str] = None
    errors: List[str] = None


class ParserBase(ABC):
    """Abstract base class for file parsers."""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """File extensions this parser handles."""
        pass
    
    @property
    @abstractmethod
    def language(self) -> str:
        """Language name."""
        pass
    
    @abstractmethod
    def parse(self, content: str, path: str) -> ParseResult:
        """
        Parse file content and extract entities.
        
        Args:
            content: File content as string
            path: File path (for context)
        
        Returns:
            ParseResult with extracted entities
        """
        pass
    
    def can_parse(self, path: str) -> bool:
        """Check if this parser can handle the file."""
        return any(path.endswith(ext) for ext in self.supported_extensions)
