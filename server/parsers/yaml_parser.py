"""
YAML Parser

Parses YAML files, especially meta.yaml for CIP.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

import yaml

from .base import ParserBase, ParseResult, ParsedEntity

logger = logging.getLogger(__name__)


class YamlParser(ParserBase):
    """
    Parser for YAML files.
    
    Special handling for meta.yaml CIP files.
    """
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".yaml", ".yml"]
    
    @property
    def language(self) -> str:
        return "yaml"
    
    def parse(self, content: str, path: str) -> ParseResult:
        """Parse YAML file and extract structure."""
        entities = []
        errors = []
        
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            errors.append(f"YAML parse error: {e}")
            return ParseResult(
                path=path,
                language=self.language,
                entities=[],
                errors=errors,
            )
        
        if data is None:
            return ParseResult(
                path=path,
                language=self.language,
                entities=[],
            )
        
        # Check if this is a meta.yaml
        is_meta = path.endswith("meta.yaml") or "schema_version" in data
        
        if is_meta:
            entities.append(self._parse_meta_yaml(data, content, path))
        else:
            entities.append(self._parse_generic_yaml(data, content, path))
        
        return ParseResult(
            path=path,
            language=self.language,
            entities=entities,
            errors=errors if errors else None,
        )
    
    def _parse_meta_yaml(
        self,
        data: Dict[str, Any],
        content: str,
        path: str,
    ) -> ParsedEntity:
        """Parse a CIP meta.yaml file."""
        lines = content.split("\n")
        
        # Extract key CIP fields
        description = data.get("description", "")
        schema_version = data.get("schema_version", "unknown")
        semantic_scope = data.get("semantic_scope")
        proficiency_level = data.get("proficiency_level")
        
        # Get files list if present
        files = data.get("files", [])
        children = []
        if isinstance(files, list):
            for f in files:
                if isinstance(f, dict):
                    children.extend(f.keys())
                elif isinstance(f, str):
                    children.append(f)
        
        return ParsedEntity(
            type="meta_yaml",
            name=path.split("/")[-2] if "/" in path else "root",
            content=content,
            line_start=1,
            line_end=len(lines),
            docstring=description,
            children=children if children else None,
            metadata={
                "schema_version": schema_version,
                "semantic_scope": semantic_scope,
                "proficiency_level": proficiency_level,
                "raw_data": data,
            },
        )
    
    def _parse_generic_yaml(
        self,
        data: Dict[str, Any],
        content: str,
        path: str,
    ) -> ParsedEntity:
        """Parse a generic YAML file."""
        lines = content.split("\n")
        
        # Get top-level keys
        keys = list(data.keys()) if isinstance(data, dict) else []
        
        return ParsedEntity(
            type="yaml_document",
            name=path.split("/")[-1],
            content=content,
            line_start=1,
            line_end=len(lines),
            children=keys if keys else None,
            metadata={"raw_data": data},
        )
