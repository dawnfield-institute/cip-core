"""
CIP filename tagging schema validation.

Validates the CIP filename tagging convention:
[m][D][v1.0][C1][I1]_filename.md

Where:
- [m] = Milestone/Module identifier
- [D] = Document type (D=doc, E=experiment, etc.)
- [v1.0] = Version
- [C1] = Chapter/Category
- [I1] = Item/Index
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class FilenameTag:
    """Parsed CIP filename tag."""
    milestone: str
    doc_type: str
    version: str
    chapter: str
    item: str
    base_name: str


class FilenameTagSchema:
    """Validator for CIP filename tagging conventions."""
    
    # Pattern for CIP filename tags
    PATTERN = r'\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]\[([^\]]+)\]_(.+)'
    
    def validate_filename(self, filename: str) -> Tuple[bool, Optional[FilenameTag]]:
        """
        Validate and parse CIP filename tags.
        
        Returns:
            (is_valid, parsed_tag_or_none)
        """
        match = re.match(self.PATTERN, filename)
        if not match:
            return False, None
        
        groups = match.groups()
        tag = FilenameTag(
            milestone=groups[0],
            doc_type=groups[1], 
            version=groups[2],
            chapter=groups[3],
            item=groups[4],
            base_name=groups[5]
        )
        
        return True, tag
    
    def generate_filename(self, tag: FilenameTag, extension: str = ".md") -> str:
        """Generate filename from tag components."""
        return f"[{tag.milestone}][{tag.doc_type}][{tag.version}][{tag.chapter}][{tag.item}]_{tag.base_name}{extension}"
