"""Tests for Kronos types."""

import pytest
from datetime import datetime

from kronos.types import (
    NodeType,
    RelationType,
    RepoNode,
    RepoEdge,
    QueryResult,
)


class TestNodeType:
    """Test NodeType enum."""
    
    def test_file_type(self):
        assert NodeType.FILE.value == "FILE"
    
    def test_function_type(self):
        assert NodeType.FUNCTION.value == "FUNCTION"
    
    def test_all_types_are_strings(self):
        for node_type in NodeType:
            assert isinstance(node_type.value, str)


class TestRelationType:
    """Test RelationType enum."""
    
    def test_contains(self):
        assert RelationType.CONTAINS.value == "CONTAINS"
    
    def test_evolves_from(self):
        assert RelationType.EVOLVES_FROM.value == "EVOLVES_FROM"


class TestRepoNode:
    """Test RepoNode dataclass."""
    
    def test_create_node(self):
        node = RepoNode(
            id="test-1",
            type=NodeType.FILE,
            path="src/main.py",
            content="print('hello')",
        )
        
        assert node.id == "test-1"
        assert node.type == NodeType.FILE
        assert node.path == "src/main.py"
    
    def test_to_dict(self):
        node = RepoNode(
            id="test-1",
            type=NodeType.FUNCTION,
            path="src/utils.py",
            content="def hello(): pass",
            name="hello",
        )
        
        data = node.to_dict()
        
        assert data["id"] == "test-1"
        assert data["type"] == "FUNCTION"
        assert data["name"] == "hello"
    
    def test_from_dict(self):
        data = {
            "id": "test-2",
            "type": "CLASS",
            "path": "src/models.py",
            "content": "class User: pass",
            "created_at": "2025-01-01T00:00:00",
        }
        
        node = RepoNode.from_dict(data)
        
        assert node.id == "test-2"
        assert node.type == NodeType.CLASS
        assert node.path == "src/models.py"


class TestRepoEdge:
    """Test RepoEdge dataclass."""
    
    def test_create_edge(self):
        edge = RepoEdge(
            id="edge-1",
            from_id="node-1",
            to_id="node-2",
            relation=RelationType.CONTAINS,
        )
        
        assert edge.from_id == "node-1"
        assert edge.to_id == "node-2"
        assert edge.relation == RelationType.CONTAINS
        assert edge.weight == 1.0
    
    def test_to_dict(self):
        edge = RepoEdge(
            id="edge-1",
            from_id="node-1",
            to_id="node-2",
            relation=RelationType.IMPORTS,
            weight=0.8,
        )
        
        data = edge.to_dict()
        
        assert data["relation"] == "IMPORTS"
        assert data["weight"] == 0.8


class TestQueryResult:
    """Test QueryResult dataclass."""
    
    def test_strength_uses_score(self):
        node = RepoNode(
            id="test",
            type=NodeType.FILE,
            path="test.py",
            content="test",
        )
        result = QueryResult(node=node, score=0.9)
        
        assert result.strength == 0.9
    
    def test_strength_uses_path_strength(self):
        node = RepoNode(
            id="test",
            type=NodeType.FILE,
            path="test.py",
            content="test",
        )
        result = QueryResult(
            node=node,
            score=0.9,
            path_strength=0.7,
        )
        
        assert result.strength == 0.7
