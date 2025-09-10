"""
Repository-level schema validation for CIP compliance.
"""

from typing import Dict, Any, List
from pathlib import Path


class RepositorySchema:
    """
    Validates overall repository structure and organization
    according to CIP specifications.
    """
    
    def __init__(self):
        self.required_files = [".cip/meta.yaml"]
        self.recommended_files = ["README.md", "LICENSE"]
    
    def validate_structure(self, repo_path: Path) -> Dict[str, Any]:
        """
        Validate repository structure.
        
        Returns validation results with suggestions.
        """
        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check required files
        for required_file in self.required_files:
            file_path = repo_path / required_file
            if not file_path.exists():
                results["valid"] = False
                results["errors"].append(f"Missing required file: {required_file}")
        
        # Check recommended files
        for recommended_file in self.recommended_files:
            file_path = repo_path / recommended_file
            if not file_path.exists():
                results["warnings"].append(f"Missing recommended file: {recommended_file}")
        
        return results
