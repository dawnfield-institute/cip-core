"""Pytest configuration and fixtures for server tests."""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_python_code():
    """Sample Python code for parser testing."""
    return '''
"""Module docstring."""

import os
from pathlib import Path


class SampleClass:
    """A sample class for testing."""
    
    def __init__(self, name: str):
        """Initialize the class."""
        self.name = name
    
    def get_name(self) -> str:
        """Get the name."""
        return self.name


def sample_function(x: int, y: int) -> int:
    """Add two numbers.
    
    Args:
        x: First number
        y: Second number
    
    Returns:
        The sum of x and y
    """
    return x + y


def helper():
    """A helper function."""
    result = sample_function(1, 2)
    return result
'''


@pytest.fixture
def sample_markdown():
    """Sample Markdown for parser testing."""
    return '''
# Main Heading

This is some content.

## Section 1

Content for section 1 with a [link](https://example.com).

### Subsection 1.1

More content here.

## Section 2

Content for section 2.

```python
def code_example():
    pass
```

Another [internal link](../other.md).
'''


@pytest.fixture
def sample_meta_yaml():
    """Sample meta.yaml for parser testing."""
    return '''
schema_version: "3.0"
description: "Test module for validation"
semantic_scope: "implementation"
proficiency_level: "intermediate"
estimated_context_weight: 500

files:
  - "[main.py]": "Main entry point"
  - "[utils.py]": "Utility functions"

child_directories:
  - "[tests/]": "Test suite"

validation_type: "schema_v3"
'''


@pytest.fixture
async def mock_storage():
    """Create a mock Kronos storage for testing."""
    from unittest.mock import AsyncMock, MagicMock
    
    storage = AsyncMock()
    storage.connect = AsyncMock()
    storage.close = AsyncMock()
    storage.health_check = AsyncMock(return_value={"graph": True, "vector": True})
    storage.store_node = AsyncMock(return_value="node_123")
    storage.create_edge = AsyncMock()
    storage.query = AsyncMock(return_value=[
        {
            "id": "node_1",
            "type": "function",
            "path": "test.py#func",
            "content": "def func():",
            "metadata": {},
            "score": 0.95
        }
    ])
    storage.get_node = AsyncMock(return_value={
        "id": "node_1",
        "type": "function",
        "path": "test.py#func",
        "content": "def func():",
        "metadata": {}
    })
    storage.get_edges = AsyncMock(return_value=[
        {"from_id": "node_1", "to_id": "node_2", "relation": "CALLS"}
    ])
    
    return storage


@pytest.fixture
def sample_config():
    """Sample server configuration."""
    return {
        "host": "127.0.0.1",
        "port": 8000,
        "debug": False,
        "storage": {
            "graph_backend": "sqlite",
            "vector_backend": "chromadb",
            "graph_uri": "sqlite:///:memory:",
            "vector_uri": ":memory:",
            "embedding_model": "all-MiniLM-L6-v2"
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
            "api_key": None
        },
        "webhook": {
            "enabled": True,
            "github_secret": "test-secret",
            "gitlab_token": None
        },
        "repos": []
    }
