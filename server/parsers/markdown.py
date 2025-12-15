"""
Markdown Parser

Extracts sections and structure from Markdown files.
"""

from __future__ import annotations

import re
import logging
from typing import List

from .base import ParserBase, ParseResult, ParsedEntity

logger = logging.getLogger(__name__)


class MarkdownParser(ParserBase):
    """
    Parser for Markdown files.
    
    Extracts headings, sections, and links.
    """
    
    # Regex patterns
    HEADING_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    CODE_BLOCK_PATTERN = re.compile(r'^```(\w+)?$', re.MULTILINE)
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".md", ".markdown"]
    
    @property
    def language(self) -> str:
        return "markdown"
    
    def parse(self, content: str, path: str) -> ParseResult:
        """Parse Markdown file and extract sections."""
        entities = []
        lines = content.split("\n")
        
        # Find all headings
        headings = []
        for i, line in enumerate(lines):
            match = self.HEADING_PATTERN.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append({
                    "level": level,
                    "title": title,
                    "line": i + 1,
                })
        
        # Extract sections based on headings
        for i, heading in enumerate(headings):
            # Determine section end
            if i + 1 < len(headings):
                end_line = headings[i + 1]["line"] - 1
            else:
                end_line = len(lines)
            
            # Get section content
            section_lines = lines[heading["line"] - 1:end_line]
            content_text = "\n".join(section_lines)
            
            # Find parent (previous heading with lower level)
            parent = None
            for j in range(i - 1, -1, -1):
                if headings[j]["level"] < heading["level"]:
                    parent = headings[j]["title"]
                    break
            
            entities.append(ParsedEntity(
                type="section",
                name=heading["title"],
                content=content_text,
                line_start=heading["line"],
                line_end=end_line,
                parent=parent,
                metadata={
                    "level": heading["level"],
                    "links": self._extract_links(content_text),
                },
            ))
        
        # If no headings, treat entire file as one section
        if not entities:
            entities.append(ParsedEntity(
                type="document",
                name=path.split("/")[-1],
                content=content,
                line_start=1,
                line_end=len(lines),
                metadata={
                    "links": self._extract_links(content),
                },
            ))
        
        return ParseResult(
            path=path,
            language=self.language,
            entities=entities,
        )
    
    def _extract_links(self, content: str) -> List[dict]:
        """Extract links from content."""
        links = []
        for match in self.LINK_PATTERN.finditer(content):
            links.append({
                "text": match.group(1),
                "url": match.group(2),
            })
        return links
