"""Tests for Validation API endpoints."""

import pytest
import sys
from pathlib import Path
from httpx import AsyncClient, ASGITransport

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.validation import ValidationService


@pytest.fixture
def test_app():
    """Create a test FastAPI app with services."""
    from fastapi import FastAPI
    from api import register_routers
    
    app = FastAPI()
    
    # Initialize services
    app.state.services = {}
    app.state.services['validation'] = ValidationService()
    
    register_routers(app)
    
    return app


@pytest.fixture
async def client(test_app):
    """Create test client."""
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_validate_repo_endpoint(client):
    """Test /api/validate/repo endpoint."""
    # Use cip-core repo
    repo_path = str(Path(__file__).parent.parent.parent)
    
    response = await client.post(
        "/api/validate/repo",
        json={
            "path": repo_path,
            "checks": ["compliance"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "valid" in data
    assert "score" in data
    assert "errors" in data
    assert "warnings" in data
    
    # cip-core should have high compliance
    assert data["score"] >= 0.8
    
    print(f"\nCompliance Score: {data['score']:.2%}")
    print(f"Errors: {len(data['errors'])}")
    print(f"Warnings: {len(data['warnings'])}")


@pytest.mark.asyncio
async def test_validate_meta_valid(client):
    """Test /api/validate/meta with valid content."""
    response = await client.post(
        "/api/validate/meta",
        json={
            "schema_version": "2.0",
            "description": "Test repository",
            "semantic_scope": "implementation",
            "proficiency_level": "intermediate"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "valid" in data
    assert "errors" in data
    assert "warnings" in data


@pytest.mark.asyncio
async def test_validate_meta_missing_required(client):
    """Test /api/validate/meta with missing required fields."""
    response = await client.post(
        "/api/validate/meta",
        json={
            "description": "Missing schema_version"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have errors
    assert len(data["errors"]) > 0


@pytest.mark.asyncio
async def test_validate_structure_endpoint(client):
    """Test /api/validate/structure endpoint."""
    repo_path = str(Path(__file__).parent.parent.parent)
    
    response = await client.post(
        "/api/validate/structure",
        json={
            "path": repo_path,
            "checks": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "valid" in data
    assert "errors" in data
    assert "warnings" in data


@pytest.mark.asyncio
async def test_validate_file_endpoint(client):
    """Test /api/validate/file with uploaded YAML."""
    # Create a valid meta.yaml file content
    yaml_content = """schema_version: "2.0"
description: "Test repository"
semantic_scope: "implementation"
proficiency_level: "intermediate"
"""
    
    files = {
        "file": ("meta.yaml", yaml_content.encode(), "application/x-yaml")
    }
    
    response = await client.post(
        "/api/validate/file",
        files=files
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "valid" in data
    assert "errors" in data


@pytest.mark.asyncio
async def test_validate_file_invalid_yaml(client):
    """Test /api/validate/file with invalid YAML."""
    # Invalid YAML syntax
    yaml_content = """schema_version: "2.0
description: "Missing closing quote
"""
    
    files = {
        "file": ("meta.yaml", yaml_content.encode(), "application/x-yaml")
    }
    
    response = await client.post(
        "/api/validate/file",
        files=files
    )
    
    # Should return 400 for invalid YAML
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
