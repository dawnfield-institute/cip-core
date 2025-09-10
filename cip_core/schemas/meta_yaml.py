"""
CIP meta.yaml schema validation and parsing.

Implements validation for the CIP metadata format that enables
cross-repository navigation and automated content discovery.
"""

import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import jsonschema
from jsonschema import validate, ValidationError


@dataclass
class ValidationResult:
    """Result of schema validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    schema_version: Optional[str] = None


class MetaYamlSchema:
    """
    Validator for CIP meta.yaml files.
    
    Supports multiple schema versions and provides detailed
    validation feedback for automated workflows.
    """
    
    # CIP 2.0 Schema Definition
    SCHEMA_2_0 = {
        "type": "object",
        "required": ["schema_version", "repository_role"],
        "properties": {
            "schema_version": {
                "type": "string",
                "enum": ["2.0", "2.1"]
            },
            "repository_role": {
                "type": "string", 
                "enum": [
                    "theory",
                    "sdk", 
                    "devkit",
                    "models",
                    "protocol",
                    "infrastructure",
                    "ecosystem_coordinator"
                ]
            },
            "title": {"type": "string"},
            "description": {"type": "string"},
            "version": {"type": "string"},
            "authors": {
                "type": "array",
                "items": {"type": "string"}
            },
            "license": {"type": "string"},
            "ecosystem_links": {
                "type": "object",
                "additionalProperties": {
                    "type": "string",
                    "pattern": "^repo://.*"
                }
            },
            "dependencies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "type"],
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "version": {"type": "string"},
                        "repository": {"type": "string"}
                    }
                }
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "cognition_metrics": {
                "type": "object",
                "properties": {
                    "complexity_score": {"type": "number"},
                    "comprehension_baseline": {"type": "number"},
                    "last_benchmark": {"type": "string"}
                }
            }
        },
        "additionalProperties": True
    }
    
    def __init__(self):
        self.schemas = {
            "2.0": self.SCHEMA_2_0,
            "2.1": self.SCHEMA_2_0  # Same for now
        }
    
    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a meta.yaml file against CIP schema.
        
        Args:
            file_path: Path to the meta.yaml file
            
        Returns:
            ValidationResult with validation status and feedback
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return self.validate_data(data)
            
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                errors=[f"File not found: {file_path}"],
                warnings=[]
            )
        except yaml.YAMLError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"YAML parsing error: {str(e)}"],
                warnings=[]
            )
    
    def validate_data(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate parsed YAML data against CIP schema.
        
        Args:
            data: Parsed YAML data
            
        Returns:
            ValidationResult with validation status and feedback
        """
        errors = []
        warnings = []
        
        # Check schema version
        schema_version = data.get("schema_version")
        if not schema_version:
            errors.append("Missing required field: schema_version")
            return ValidationResult(False, errors, warnings)
        
        if schema_version not in self.schemas:
            errors.append(f"Unsupported schema version: {schema_version}")
            return ValidationResult(False, errors, warnings)
        
        # Validate against schema
        try:
            validate(instance=data, schema=self.schemas[schema_version])
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return ValidationResult(False, errors, warnings)
        
        # Additional CIP-specific validations
        warnings.extend(self._validate_ecosystem_links(data))
        warnings.extend(self._validate_repository_role(data))
        
        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            schema_version=schema_version
        )
    
    def _validate_ecosystem_links(self, data: Dict[str, Any]) -> List[str]:
        """Validate ecosystem_links follow repo:// convention."""
        warnings = []
        
        ecosystem_links = data.get("ecosystem_links", {})
        for key, value in ecosystem_links.items():
            if not value.startswith("repo://"):
                warnings.append(f"Ecosystem link '{key}' should use repo:// scheme: {value}")
        
        return warnings
    
    def _validate_repository_role(self, data: Dict[str, Any]) -> List[str]:
        """Validate repository role makes sense for the content."""
        warnings = []
        
        role = data.get("repository_role")
        title = data.get("title", "").lower()
        
        # Heuristic validation
        if role == "theory" and "sdk" in title:
            warnings.append("Repository role 'theory' but title suggests SDK content")
        elif role == "sdk" and "theory" in title:
            warnings.append("Repository role 'sdk' but title suggests theoretical content")
        
        return warnings
    
    def generate_template(self, repository_role: str, **kwargs) -> Dict[str, Any]:
        """
        Generate a template meta.yaml for a given repository role.
        
        Args:
            repository_role: The role of the repository
            **kwargs: Additional fields to include
            
        Returns:
            Dictionary representing meta.yaml template
        """
        template = {
            "schema_version": "2.0",
            "repository_role": repository_role,
            "title": kwargs.get("title", f"Dawn Field {repository_role.title()}"),
            "description": kwargs.get("description", f"Dawn Field Theory {repository_role} component"),
            "version": kwargs.get("version", "0.1.0"),
            "authors": kwargs.get("authors", ["Dawn Field Institute"]),
            "license": kwargs.get("license", "Under Review"),
            "tags": kwargs.get("tags", [repository_role, "dawn-field-theory"]),
        }
        
        # Add role-specific defaults
        if repository_role in ["sdk", "devkit", "models"]:
            template["ecosystem_links"] = {
                "theory": "repo://dawn-field-theory/foundational/",
                "protocol": "repo://cip-core/"
            }
        elif repository_role == "theory":
            template["ecosystem_links"] = {
                "protocol": "repo://cip-core/",
                "sdk": "repo://fracton-sdk/"
            }
        
        return template
