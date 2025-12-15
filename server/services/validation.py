"""Validation Service - CIP compliance validation."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ValidationIssue:
    """A validation error or warning."""
    level: str  # "error" or "warning"
    code: str
    message: str
    path: Optional[str] = None
    line: Optional[int] = None


@dataclass  
class ValidationResult:
    """Result of validation."""
    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    score: float = 0.0


class ValidationService:
    """
    Service for validating CIP compliance.
    
    Wraps existing cip_core.validators.
    """
    
    def __init__(self):
        """Initialize validation service."""
        # Import existing validators
        try:
            from cip_core.validators import ComplianceValidator
            self.compliance_validator = ComplianceValidator()
        except ImportError:
            self.compliance_validator = None
    
    async def validate_repo(
        self,
        path: str,
        checks: list[str] = None
    ) -> ValidationResult:
        """
        Validate an entire repository.
        
        checks: ["meta", "structure", "schema", "compliance"]
        """
        if checks is None:
            checks = ["meta", "structure", "schema"]
        
        errors = []
        warnings = []
        
        # TODO: Implement full validation using cip_core
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def validate_meta(self, content: dict) -> ValidationResult:
        """Validate meta.yaml content."""
        errors = []
        warnings = []
        
        # Check required fields
        required = ["schema_version", "description"]
        for field in required:
            if field not in content:
                errors.append(ValidationIssue(
                    level="error",
                    code="MISSING_REQUIRED",
                    message=f"Missing required field: {field}"
                ))
        
        # TODO: Full schema validation
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def validate_structure(self, path: str) -> ValidationResult:
        """Validate repository structure."""
        # TODO: Implement
        return ValidationResult(valid=True)
    
    async def validate_schema(
        self,
        content: dict,
        schema_version: str = "2.0"
    ) -> ValidationResult:
        """Validate against specific schema version."""
        # TODO: Implement
        return ValidationResult(valid=True)
