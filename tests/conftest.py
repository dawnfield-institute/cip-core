"""
Pytest fixtures for CIP-Core tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml

from cip_core.schemas import MetaYamlSchema
from cip_core.validators import ComplianceValidator


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir)
        yield repo_path


@pytest.fixture
def sample_meta_yaml():
    """Sample valid meta.yaml data."""
    return {
        "schema_version": "2.0",
        "repository_role": "theory",
        "title": "Test Repository",
        "description": "A test repository for unit testing",
        "version": "1.0.0",
        "authors": ["Test Author <test@example.com>"],
        "license": "MIT",
        "created": "2025-09-10",
        "last_updated": "2025-09-10"
    }


@pytest.fixture
def cip_repo(temp_repo, sample_meta_yaml):
    """Create a temporary repository with basic CIP structure."""
    # Create .cip directory
    cip_dir = temp_repo / ".cip"
    cip_dir.mkdir()
    
    # Create meta.yaml
    with open(cip_dir / "meta.yaml", "w") as f:
        yaml.dump(sample_meta_yaml, f, default_flow_style=False)
    
    # Create core.yaml with basic structure
    core_data = {
        "schema_version": "2.0",
        "repository_structure": {
            "src/": {
                "description": "Source code directory",
                "type": "directory"
            },
            "tests/": {
                "description": "Test files",
                "type": "directory"
            }
        }
    }
    
    with open(cip_dir / "core.yaml", "w") as f:
        yaml.dump(core_data, f, default_flow_style=False)
    
    # Create basic files
    (temp_repo / "README.md").write_text("# Test Repository\n\nThis is a test repository.")
    (temp_repo / "src").mkdir()
    (temp_repo / "src" / "main.py").write_text("# Main module\nprint('Hello, World!')")
    (temp_repo / "tests").mkdir()
    (temp_repo / "tests" / "test_main.py").write_text("# Test module\ndef test_hello():\n    pass")
    
    return temp_repo


@pytest.fixture
def meta_yaml_schema():
    """Meta YAML schema instance."""
    return MetaYamlSchema()


@pytest.fixture
def compliance_validator():
    """Compliance validator instance."""
    return ComplianceValidator()


@pytest.fixture
def invalid_meta_yaml():
    """Sample invalid meta.yaml data for testing validation failures."""
    return {
        "schema_version": "1.0",  # Old version
        "title": "",  # Empty title
        "description": "Generic description",  # Generic
        # Missing required fields
    }


@pytest.fixture
def large_repo_structure():
    """Sample data for testing large repository structures."""
    structure = {}
    
    # Create a nested structure with many directories
    for i in range(10):
        dir_name = f"module_{i:02d}/"
        structure[dir_name] = {
            "description": f"Module {i} with specific functionality",
            "type": "directory"
        }
        
        # Add subdirectories
        for j in range(5):
            subdir_name = f"module_{i:02d}/submodule_{j:02d}/"
            structure[subdir_name] = {
                "description": f"Submodule {j} of module {i}",
                "type": "directory"
            }
    
    return {
        "schema_version": "2.0",
        "repository_structure": structure
    }


@pytest.fixture(scope="session")
def ai_available():
    """Check if AI (Ollama) is available for testing."""
    try:
        from cip_core.ollama_local.client import OllamaClient
        client = OllamaClient()
        # Try to connect to Ollama
        models = client.list_models()
        return len(models) > 0
    except Exception:
        return False


class MockOllamaClient:
    """Mock Ollama client for testing without actual AI."""
    
    def __init__(self):
        self.responses = {
            "describe_directory": "This is a test directory containing sample code and utilities",
            "generate_instructions": "This repository contains test code. Please follow standard Python practices.",
        }
    
    def describe_directory(self, path, files):
        return self.responses["describe_directory"]
    
    def generate_instructions(self, repo_structure):
        return self.responses["generate_instructions"]
    
    def list_models(self):
        return ["mock-model:latest"]


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    return MockOllamaClient()
