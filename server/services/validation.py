"""Validation Service - CIP compliance validation."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


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
            from cip_core.validators.compliance import ComplianceValidator
            from cip_core.validators.metadata import MetadataValidator
            from cip_core.validators.cross_repo import CrossRepoValidator
            
            self.compliance_validator = ComplianceValidator()
            self.metadata_validator = MetadataValidator()
            self.cross_repo_validator = CrossRepoValidator()
            logger.info("Validators initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import validators: {e}")
            self.compliance_validator = None
            self.metadata_validator = None
            self.cross_repo_validator = None
    
    async def validate_repo(
        self,
        path: str,
        checks: list[str] = None
    ) -> ValidationResult:
        """
        Validate an entire repository.
        
        Args:
            path: Path to repository root
            checks: Optional list of specific checks to run
                   ["meta", "structure", "schema", "compliance"]
                   If None, runs all checks
        
        Returns:
            ValidationResult with validation status and issues
        """
        if checks is None:
            checks = ["compliance"]  # Run full compliance validation by default
        
        if not self.compliance_validator:
            return ValidationResult(
                valid=False,
                errors=[ValidationIssue(
                    level="error",
                    code="VALIDATOR_UNAVAILABLE",
                    message="ComplianceValidator not available"
                )],
                score=0.0
            )
        
        try:
            # Use cip_core's ComplianceValidator
            report = self.compliance_validator.validate_repository(path)
            
            # Convert ComplianceIssues to ValidationIssues
            errors = []
            warnings = []
            
            for issue in report.issues:
                val_issue = ValidationIssue(
                    level=issue.level,
                    code=issue.category.upper(),
                    message=issue.message,
                    path=issue.file_path
                )
                
                if issue.level == "error":
                    errors.append(val_issue)
                elif issue.level == "warning":
                    warnings.append(val_issue)
            
            return ValidationResult(
                valid=report.is_compliant,
                errors=errors,
                warnings=warnings,
                score=report.score
            )
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return ValidationResult(
                valid=False,
                errors=[ValidationIssue(
                    level="error",
                    code="VALIDATION_ERROR",
                    message=f"Validation failed: {str(e)}"
                )],
                score=0.0
            )
    
    async def validate_meta(self, content: dict) -> ValidationResult:
        """
        Validate meta.yaml content using schema validator.
        
        Args:
            content: Parsed meta.yaml dictionary
            
        Returns:
            ValidationResult with validation status
        """
        try:
            from cip_core.schemas import MetaYamlSchema
            
            schema = MetaYamlSchema()
            
            # Create temporary file to validate (schema expects file path)
            import tempfile
            import yaml
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(content, f)
                temp_path = f.name
            
            try:
                # Validate using schema
                result = schema.validate_file_with_context(temp_path, is_root=False)
                
                errors = []
                warnings = []
                
                # Convert schema errors to ValidationIssues
                for error in result.errors:
                    errors.append(ValidationIssue(
                        level="error",
                        code="SCHEMA_ERROR",
                        message=error
                    ))
                
                for warning in result.warnings:
                    warnings.append(ValidationIssue(
                        level="warning",
                        code="SCHEMA_WARNING",
                        message=warning
                    ))
                
                return ValidationResult(
                    valid=result.is_valid,
                    errors=errors,
                    warnings=warnings
                )
            finally:
                # Clean up temp file
                import os
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Meta validation failed: {e}")
            return ValidationResult(
                valid=False,
                errors=[ValidationIssue(
                    level="error",
                    code="VALIDATION_ERROR",
                    message=f"Meta validation failed: {str(e)}"
                )]
            )
    
    async def validate_structure(self, path: str) -> ValidationResult:
        """
        Validate repository structure (README, LICENSE, etc).
        
        Uses ComplianceValidator's structure checks.
        """
        if not self.compliance_validator:
            return ValidationResult(
                valid=False,
                errors=[ValidationIssue(
                    level="error",
                    code="VALIDATOR_UNAVAILABLE",
                    message="ComplianceValidator not available"
                )]
            )
        
        try:
            # Run full validation and extract structure issues
            report = self.compliance_validator.validate_repository(path)
            
            errors = []
            warnings = []
            
            # Filter for structure-related issues only
            for issue in report.issues:
                if issue.category == "structure":
                    val_issue = ValidationIssue(
                        level=issue.level,
                        code="STRUCTURE",
                        message=issue.message,
                        path=issue.file_path
                    )
                    if issue.level == "error":
                        errors.append(val_issue)
                    elif issue.level == "warning":
                        warnings.append(val_issue)
            
            return ValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            return ValidationResult(
                valid=False,
                errors=[ValidationIssue(
                    level="error",
                    code="VALIDATION_ERROR",
                    message=f"Structure validation failed: {str(e)}"
                )]
            )
    
    async def validate_schema(
        self,
        content: dict,
        schema_version: str = "2.0"
    ) -> ValidationResult:
        """
        Validate against specific schema version.
        
        Args:
            content: Parsed YAML content
            schema_version: CIP schema version to validate against
            
        Returns:
            ValidationResult
        """
        # For now, delegate to validate_meta since it handles schema validation
        return await self.validate_meta(content)
