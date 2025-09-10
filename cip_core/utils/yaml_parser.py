"""
YAML parsing utilities.
"""

import yaml
from typing import Dict, Any, Union
from pathlib import Path


class YamlParser:
    """Safe YAML parsing with validation."""
    
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse YAML file safely."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def parse_string(self, yaml_string: str) -> Dict[str, Any]:
        """Parse YAML string safely."""
        return yaml.safe_load(yaml_string)
