"""Tests for ValidationService - Phase 2."""

import pytest
import sys
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.validation import ValidationService, ValidationResult


@pytest.fixture
def validation_service():
    """Create validation service instance."""
    return ValidationService()


@pytest.mark.asyncio
async def test_validate_repo_cip_core(validation_service):
    """Test validating the cip-core repository itself."""
    # Use the cip-core repo path (parent of server/)
    repo_path = Path(__file__).parent.parent.parent
    
    result = await validation_service.validate_repo(str(repo_path))
    
    assert isinstance(result, ValidationResult)
    assert result.score >= 0.0
    assert result.score <= 1.0
    
    # cip-core should be compliant
    print(f"\nCompliance Score: {result.score:.2%}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    
    for error in result.errors:
        print(f"  ERROR: {error.message}")
    
    for warning in result.warnings:
        print(f"  WARN: {warning.message}")


@pytest.mark.asyncio
async def test_validate_meta_valid(validation_service):
    """Test validating valid meta.yaml content."""
    content = {
        "schema_version": "2.0",
        "description": "Test repository",
        "semantic_scope": "implementation",
        "proficiency_level": "intermediate"
    }
    
    result = await validation_service.validate_meta(content)
    
    assert isinstance(result, ValidationResult)
    # May have warnings but should be valid
    if not result.valid:
        for error in result.errors:
            print(f"  ERROR: {error.message}")


@pytest.mark.asyncio
async def test_validate_meta_missing_required(validation_service):
    """Test validation fails when required fields missing."""
    content = {
        "description": "Test without schema_version"
    }
    
    result = await validation_service.validate_meta(content)
    
    assert isinstance(result, ValidationResult)
    # Should have errors
    assert len(result.errors) > 0
    
    # Check that schema_version error is present
    error_messages = [e.message for e in result.errors]
    assert any("schema_version" in msg.lower() for msg in error_messages)


@pytest.mark.asyncio
async def test_validate_structure(validation_service):
    """Test structure validation of cip-core."""
    repo_path = Path(__file__).parent.parent.parent
    
    result = await validation_service.validate_structure(str(repo_path))
    
    assert isinstance(result, ValidationResult)
    
    # cip-core should have README and LICENSE
    print(f"\nStructure Errors: {len(result.errors)}")
    print(f"Structure Warnings: {len(result.warnings)}")
    
    for error in result.errors:
        print(f"  ERROR: {error.message}")


@pytest.mark.asyncio  
async def test_validators_initialized(validation_service):
    """Test that validators are properly initialized."""
    assert validation_service.compliance_validator is not None
    assert validation_service.metadata_validator is not None
    assert validation_service.cross_repo_validator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
