"""
Unified validation engine.

This module provides the ValidationEngine class that consolidates and replaces
multiple scattered validators with a unified interface accessible through CIPEngine.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..engine.repository import RepositoryManager
from ..engine.config import ValidationRules
from ..engine.core import ValidationResult
from ..validators import ComplianceValidator, MetadataValidator, CrossRepoValidator


class ValidationEngine:
    """
    Unified system for all CIP validation operations.
    
    This class consolidates and replaces direct usage of:
    - ComplianceValidator
    - MetadataValidator  
    - CrossRepoValidator
    
    Usage:
        engine = ValidationEngine(repo_manager)
        result = engine.validate(validation_rules)
    """
    
    def __init__(self, repo: RepositoryManager):
        """
        Initialize validation engine.
        
        Args:
            repo: Repository manager instance
        """
        self.repo = repo
        
        # Initialize underlying validators (lazy loading)
        self._compliance_validator = None
        self._metadata_validator = None
        self._cross_repo_validator = None
    
    @property
    def compliance(self):
        """Get compliance validator (lazy loaded)."""
        if self._compliance_validator is None:
            self._compliance_validator = ComplianceValidator()
        return self._compliance_validator
    
    @property
    def metadata(self):
        """Get metadata validator (lazy loaded)."""
        if self._metadata_validator is None:
            self._metadata_validator = MetadataValidator()
        return self._metadata_validator
    
    @property
    def cross_repo(self):
        """Get cross-repository validator (lazy loaded)."""
        if self._cross_repo_validator is None:
            self._cross_repo_validator = CrossRepoValidator()
        return self._cross_repo_validator
    
    def validate(self, rules: ValidationRules) -> ValidationResult:
        """
        Perform comprehensive validation using specified rules.
        
        Args:
            rules: Validation rules configuration
            
        Returns:
            ValidationResult with comprehensive validation report
        """
        all_issues = []
        total_checks = 0
        passed_checks = 0
        
        try:
            # 1. Compliance validation
            if 'compliance' in rules.enabled_rules:
                compliance_report = self.compliance.validate_repository(str(self.repo.path))
                all_issues.extend([
                    {
                        'level': issue.level,
                        'category': issue.category,
                        'message': issue.message,
                        'file_path': issue.file_path,
                        'suggested_fix': issue.suggested_fix
                    }
                    for issue in compliance_report.issues
                ])
                total_checks += compliance_report.total_checks
                passed_checks += compliance_report.passed_checks
            
            # 2. Schema validation
            if 'schema' in rules.enabled_rules:
                # Find all meta.yaml files and validate them
                from ..schemas import MetaYamlSchema
                schema_validator = MetaYamlSchema()
                
                meta_files = list(self.repo.path.rglob("meta.yaml"))
                for meta_file in meta_files:
                    try:
                        # Determine if this is a root meta.yaml
                        is_root = meta_file.parent == self.repo.path
                        
                        # Use context-aware validation
                        validation_result = schema_validator.validate_file_with_context(str(meta_file), is_root)
                        total_checks += 1
                        
                        if validation_result.is_valid:
                            passed_checks += 1
                        else:
                            for error in validation_result.errors:
                                all_issues.append({
                                    'level': 'error',
                                    'category': 'schema',
                                    'message': f'{meta_file.relative_to(self.repo.path)}: {error}',
                                    'file_path': str(meta_file),
                                    'suggested_fix': 'Fix schema validation errors'
                                })
                            
                            for warning in validation_result.warnings:
                                all_issues.append({
                                    'level': 'warning',
                                    'category': 'schema',
                                    'message': f'{meta_file.relative_to(self.repo.path)}: {warning}',
                                    'file_path': str(meta_file),
                                    'suggested_fix': 'Address schema warnings'
                                })
                                
                    except Exception as e:
                        all_issues.append({
                            'level': 'error',
                            'category': 'schema',
                            'message': f'Schema validation failed for {meta_file.relative_to(self.repo.path)}: {str(e)}',
                            'file_path': str(meta_file),
                            'suggested_fix': 'Check file format and required fields'
                        })
            
            # 3. Cross-repository validation  
            if 'cross_repo' in rules.enabled_rules:
                try:
                    cross_repo_issues = self.cross_repo.validate_repository_links(str(self.repo.path))
                    all_issues.extend([
                        {
                            'level': 'warning',
                            'category': 'cross_repo',
                            'message': issue,
                            'file_path': None,
                            'suggested_fix': 'Update repository links'
                        }
                        for issue in cross_repo_issues
                    ])
                    total_checks += 1
                    if not cross_repo_issues:
                        passed_checks += 1
                except Exception as e:
                    all_issues.append({
                        'level': 'warning',
                        'category': 'cross_repo', 
                        'message': f'Cross-repo validation failed: {str(e)}',
                        'file_path': None,
                        'suggested_fix': 'Check repository connectivity'
                    })
            
            # Calculate overall score
            if total_checks > 0:
                score = passed_checks / total_checks
            else:
                score = 1.0 if not all_issues else 0.0
            
            # Generate summary
            error_count = len([i for i in all_issues if i['level'] == 'error'])
            warning_count = len([i for i in all_issues if i['level'] == 'warning'])
            
            if error_count == 0 and warning_count == 0:
                summary = "✅ Repository is fully CIP compliant"
            elif error_count == 0:
                summary = f"⚠️ Repository is compliant with {warning_count} warnings"
            else:
                summary = f"❌ Repository has {error_count} errors and {warning_count} warnings"
            
            return ValidationResult(
                success=True,
                score=score,
                total_checks=total_checks,
                passed_checks=passed_checks,
                issues=all_issues,
                summary=summary
            )
            
        except Exception as e:
            return ValidationResult(
                success=False,
                score=0.0,
                total_checks=0,
                passed_checks=0,
                issues=[{
                    'level': 'error',
                    'category': 'system',
                    'message': f'Validation engine error: {str(e)}',
                    'file_path': None,
                    'suggested_fix': 'Check validation configuration'
                }],
                summary=f"Validation failed: {str(e)}"
            )
    
    def validate_compliance_only(self) -> ValidationResult:
        """
        Perform only compliance validation.
        
        Returns:
            ValidationResult focused on CIP compliance
        """
        rules = ValidationRules(enabled_rules=['compliance'])
        return self.validate(rules)
    
    def validate_schema_only(self) -> ValidationResult:
        """
        Perform only schema validation.
        
        Returns:
            ValidationResult focused on metadata schema compliance
        """
        rules = ValidationRules(enabled_rules=['schema'])
        return self.validate(rules)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a quick validation summary without performing full validation.
        
        Returns:
            Dictionary with basic validation metrics
        """
        return {
            'path': str(self.repo.path),
            'has_cip_setup': self.repo.cip_directory.exists(),
            'meta_files_count': len(list(self.repo.path.rglob("meta.yaml"))),
            'has_readme': (self.repo.path / "README.md").exists(),
            'project_type': self.repo.detect_project_type().value
        }
