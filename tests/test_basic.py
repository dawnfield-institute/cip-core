"""
Basic tests for CIP-Core functionality.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from cip_core.schemas import MetaYamlSchema
from cip_core.validators import ComplianceValidator
from cip_core import validate_repository


def test_meta_yaml_validation():
    """Test meta.yaml schema validation."""
    schema = MetaYamlSchema()
    
    # Valid metadata
    valid_data = {
        "schema_version": "2.0",
        "repository_role": "theory",
        "title": "Test Repository",
        "description": "A test repository",
        "version": "1.0.0",
        "authors": ["Test Author"]
    }
    
    result = schema.validate_data(valid_data)
    assert result.is_valid
    assert result.schema_version == "2.0"


def test_template_generation():
    """Test meta.yaml template generation."""
    schema = MetaYamlSchema()
    
    template = schema.generate_template(
        repository_role="sdk",
        title="Test SDK",
        license="MIT"
    )
    
    assert template["repository_role"] == "sdk"
    assert template["title"] == "Test SDK"
    assert template["license"] == "MIT"
    assert "ecosystem_links" in template


def test_compliance_validation():
    """Test basic compliance validation."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)
        
        # Create basic CIP structure
        cip_dir = repo_path / ".cip"
        cip_dir.mkdir()
        
        # Create meta.yaml
        meta_data = {
            "schema_version": "2.0",
            "repository_role": "theory",
            "title": "Test Repo"
        }
        
        with open(cip_dir / "meta.yaml", "w") as f:
            yaml.dump(meta_data, f)
        
        # Create README
        (repo_path / "README.md").write_text("# Test Repository")
        
        # Validate
        report = validate_repository(str(repo_path))
        
        assert report.score > 0.5  # Should pass basic checks
        assert len(report.issues) >= 0  # May have warnings


if __name__ == "__main__":
    # Run basic tests
    test_meta_yaml_validation()
    test_template_generation() 
    test_compliance_validation()
    print("✅ All basic tests passed!")
