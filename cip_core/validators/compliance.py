"""
CIP compliance validation engine.

Validates repositories for CIP protocol compliance including
metadata presence, file organization, and cross-repository linking.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import os

from ..schemas import MetaYamlSchema
from ..utils import YamlParser


@dataclass
class ComplianceIssue:
    """Represents a compliance validation issue."""
    level: str  # "error", "warning", "info"
    category: str  # "metadata", "structure", "links", "naming"
    message: str
    file_path: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass 
class ComplianceReport:
    """Report of CIP compliance validation."""
    score: float  # 0.0 to 1.0
    total_checks: int
    passed_checks: int
    issues: List[ComplianceIssue]
    repository_path: str
    
    @property
    def is_compliant(self) -> bool:
        """True if repository meets minimum compliance threshold."""
        return self.score >= 0.8  # 80% compliance threshold


class ComplianceValidator:
    """
    Validates repositories for CIP protocol compliance.
    
    Performs multi-level validation:
    - File-level: Individual file compliance
    - Directory-level: Folder structure and organization
    - Repository-level: Overall CIP conformance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.meta_validator = MetaYamlSchema()
        self.yaml_parser = YamlParser()
        
        # Configurable validation rules
        self.rules = {
            "require_meta_yaml": True,
            "require_readme": True,
            "require_license": True,
            "validate_ecosystem_links": True,
            "check_filename_conventions": True,
            "validate_directory_structure": True,
        }
        self.rules.update(self.config.get("rules", {}))
    
    def validate_repository(self, repo_path: str) -> ComplianceReport:
        """
        Validate entire repository for CIP compliance.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            ComplianceReport with detailed validation results
        """
        repo_path = Path(repo_path).resolve()
        issues = []
        total_checks = 0
        passed_checks = 0
        
        # Core metadata validation
        meta_yaml_path = repo_path / ".cip" / "meta.yaml"
        meta_result = self._validate_meta_yaml(meta_yaml_path)
        issues.extend(meta_result["issues"])
        total_checks += meta_result["total"]
        passed_checks += meta_result["passed"]
        
        # Repository structure validation  
        structure_result = self._validate_repository_structure(repo_path)
        issues.extend(structure_result["issues"])
        total_checks += structure_result["total"] 
        passed_checks += structure_result["passed"]
        
        # Ecosystem links validation
        if self.rules["validate_ecosystem_links"]:
            links_result = self._validate_ecosystem_links(repo_path)
            issues.extend(links_result["issues"])
            total_checks += links_result["total"]
            passed_checks += links_result["passed"]
        
        # File naming conventions
        if self.rules["check_filename_conventions"]:
            naming_result = self._validate_naming_conventions(repo_path)
            issues.extend(naming_result["issues"])
            total_checks += naming_result["total"]
            passed_checks += naming_result["passed"]
        
        # Directory metadata quality validation
        metadata_quality_result = self._validate_metadata_quality(repo_path)
        issues.extend(metadata_quality_result["issues"])
        total_checks += metadata_quality_result["total"]
        passed_checks += metadata_quality_result["passed"]
        
        # Calculate compliance score
        score = passed_checks / total_checks if total_checks > 0 else 0.0
        
        return ComplianceReport(
            score=score,
            total_checks=total_checks,
            passed_checks=passed_checks,
            issues=issues,
            repository_path=str(repo_path)
        )
    
    def _validate_meta_yaml(self, meta_path: Path) -> Dict[str, Any]:
        """Validate .cip/meta.yaml file."""
        issues = []
        total = 5  # Number of meta.yaml checks
        passed = 0
        
        if not meta_path.exists():
            if self.rules["require_meta_yaml"]:
                issues.append(ComplianceIssue(
                    level="error",
                    category="metadata", 
                    message="Missing required .cip/meta.yaml file",
                    file_path=str(meta_path),
                    suggested_fix="Run 'cip init' to generate metadata"
                ))
            return {"issues": issues, "total": total, "passed": 0}
        
        passed += 1  # File exists
        
        # Validate schema
        validation_result = self.meta_validator.validate_file(meta_path)
        
        if validation_result.is_valid:
            passed += 3  # Valid schema, required fields, format
        else:
            for error in validation_result.errors:
                issues.append(ComplianceIssue(
                    level="error",
                    category="metadata",
                    message=f"meta.yaml validation error: {error}",
                    file_path=str(meta_path)
                ))
        
        # Add warnings as info-level issues
        for warning in validation_result.warnings:
            issues.append(ComplianceIssue(
                level="warning",
                category="metadata", 
                message=f"meta.yaml warning: {warning}",
                file_path=str(meta_path)
            ))
        
        if validation_result.schema_version:
            passed += 1  # Has schema version
        
        return {"issues": issues, "total": total, "passed": passed}
    
    def _validate_repository_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Validate repository directory structure."""
        issues = []
        total = 3  # README, LICENSE, basic structure
        passed = 0
        
        # Check for README
        readme_files = list(repo_path.glob("README*"))
        if readme_files:
            passed += 1
        elif self.rules["require_readme"]:
            issues.append(ComplianceIssue(
                level="error",
                category="structure",
                message="Missing README file",
                suggested_fix="Add README.md with project description"
            ))
        
        # Check for LICENSE
        license_files = list(repo_path.glob("LICENSE*"))
        if license_files:
            passed += 1
        elif self.rules["require_license"]:
            issues.append(ComplianceIssue(
                level="warning",
                category="structure", 
                message="Missing LICENSE file",
                suggested_fix="Add LICENSE file with appropriate license"
            ))
        
        # Check for .cip directory
        cip_dir = repo_path / ".cip"
        if cip_dir.exists() and cip_dir.is_dir():
            passed += 1
        else:
            issues.append(ComplianceIssue(
                level="error",
                category="structure",
                message="Missing .cip directory",
                suggested_fix="Create .cip directory with metadata"
            ))
        
        return {"issues": issues, "total": total, "passed": passed}
    
    def _validate_ecosystem_links(self, repo_path: Path) -> Dict[str, Any]:
        """Validate ecosystem links in meta.yaml."""
        issues = []
        total = 2  # Valid links, reachable links
        passed = 0
        
        meta_path = repo_path / ".cip" / "meta.yaml"
        if not meta_path.exists():
            return {"issues": issues, "total": 0, "passed": 0}
        
        try:
            meta_data = self.yaml_parser.parse_file(meta_path)
            ecosystem_links = meta_data.get("ecosystem_links", {})
            
            if ecosystem_links:
                passed += 1  # Has ecosystem links
                
                # Validate repo:// scheme
                valid_schemes = all(
                    link.startswith("repo://") 
                    for link in ecosystem_links.values()
                )
                
                if valid_schemes:
                    passed += 1
                else:
                    issues.append(ComplianceIssue(
                        level="warning",
                        category="links",
                        message="Some ecosystem links don't use repo:// scheme",
                        file_path=str(meta_path)
                    ))
            else:
                issues.append(ComplianceIssue(
                    level="info", 
                    category="links",
                    message="No ecosystem links defined",
                    file_path=str(meta_path),
                    suggested_fix="Add ecosystem_links to connect with other repositories"
                ))
                
        except Exception as e:
            issues.append(ComplianceIssue(
                level="error",
                category="links",
                message=f"Error reading meta.yaml: {str(e)}",
                file_path=str(meta_path)
            ))
        
        return {"issues": issues, "total": total, "passed": passed}
    
    def _validate_naming_conventions(self, repo_path: Path) -> Dict[str, Any]:
        """Validate CIP filename tagging conventions."""
        issues = []
        total = 1
        passed = 0
        
        # Check for CIP filename tags in markdown files
        md_files = list(repo_path.rglob("*.md"))
        tagged_files = [f for f in md_files if self._has_cip_tags(f.name)]
        
        if tagged_files or len(md_files) == 0:
            passed += 1  # Either has tagged files or no markdown files
        else:
            issues.append(ComplianceIssue(
                level="info",
                category="naming",
                message="No CIP filename tags found in markdown files",
                suggested_fix="Consider using CIP filename tagging: [m][D][v1.0][C1][I1]_filename.md"
            ))
        
        return {"issues": issues, "total": total, "passed": passed}
    
    def _has_cip_tags(self, filename: str) -> bool:
        """Check if filename follows CIP tagging convention."""
        # Simple check for CIP tag pattern: [letter][letter]
        import re
        pattern = r'\[.\]\[.\]'
        return bool(re.search(pattern, filename))
    
    def _validate_metadata_quality(self, repo_path: Path) -> Dict[str, Any]:
        """Validate quality of directory metadata descriptions."""
        issues = []
        total = 0
        passed = 0
        
        # Generic description patterns to flag
        generic_patterns = [
            "Auto-generated metadata for",
            "auto-generated metadata for", 
            "Generated automatically",
            "Default description",
            "TODO: Add description",
            "Placeholder description"
        ]
        
        # Find all meta.yaml files in the repository
        meta_files = list(repo_path.rglob("meta.yaml"))
        
        for meta_file in meta_files:
            total += 1
            
            try:
                meta_data = self.yaml_parser.parse_file(meta_file)
                description = meta_data.get("description", "")
                
                # Check if description contains generic patterns
                is_generic = any(pattern in description for pattern in generic_patterns)
                
                if is_generic:
                    rel_path = meta_file.relative_to(repo_path)
                    issues.append(ComplianceIssue(
                        level="warning",
                        category="metadata",
                        message=f"Generic auto-generated description in {rel_path}",
                        file_path=str(meta_file),
                        suggested_fix="Use 'cip ai-metadata' to generate meaningful descriptions"
                    ))
                else:
                    passed += 1
                    
                # Also check for empty or very short descriptions
                if len(description.strip()) < 10:
                    rel_path = meta_file.relative_to(repo_path)
                    issues.append(ComplianceIssue(
                        level="info",
                        category="metadata",
                        message=f"Very short description in {rel_path}",
                        file_path=str(meta_file),
                        suggested_fix="Consider adding more descriptive content"
                    ))
                
            except Exception as e:
                rel_path = meta_file.relative_to(repo_path)
                issues.append(ComplianceIssue(
                    level="error",
                    category="metadata",
                    message=f"Error reading {rel_path}: {str(e)}",
                    file_path=str(meta_file)
                ))
        
        return {"issues": issues, "total": total, "passed": passed}
    
    def generate_compliance_summary(self, report: ComplianceReport) -> str:
        """Generate human-readable compliance summary."""
        status = "✅ COMPLIANT" if report.is_compliant else "❌ NON-COMPLIANT"
        
        summary = f"""
CIP Compliance Report
====================

Repository: {report.repository_path}
Status: {status}
Score: {report.score:.1%} ({report.passed_checks}/{report.total_checks} checks passed)

"""
        
        if report.issues:
            summary += "Issues Found:\n"
            for issue in report.issues:
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}[issue.level]
                summary += f"{icon} {issue.category.upper()}: {issue.message}\n"
                if issue.suggested_fix:
                    summary += f"   💡 {issue.suggested_fix}\n"
        else:
            summary += "✅ No issues found!\n"
        
        return summary
