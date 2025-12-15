"""Tests for SQLite graph backend."""

import pytest
import tempfile
import os
from pathlib import Path

from kronos.types import NodeType, RelationType, RepoNode, RepoEdge
from kronos.graph.sqlite import SQLiteGraphBackend


@pytest.fixture
async def db():
    """Create a temporary SQLite database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        backend = SQLiteGraphBackend(db_path)
        await backend.connect()
        yield backend
        await backend.close()


@pytest.mark.asyncio
async def test_create_and_get_node(db):
    """Test creating and retrieving a node."""
    node = RepoNode(
        id="test-node-1",
        type=NodeType.FILE,
        path="src/main.py",
        content="print('hello')",
        name="main.py",
    )
    
    await db.create_node(node)
    
    retrieved = await db.get_node("test-node-1")
    
    assert retrieved is not None
    assert retrieved.id == "test-node-1"
    assert retrieved.type == NodeType.FILE
    assert retrieved.path == "src/main.py"
    assert retrieved.name == "main.py"


@pytest.mark.asyncio
async def test_create_and_get_edge(db):
    """Test creating and retrieving edges."""
    # Create two nodes
    node1 = RepoNode(
        id="parent",
        type=NodeType.DIRECTORY,
        path="src",
        content="",
    )
    node2 = RepoNode(
        id="child",
        type=NodeType.FILE,
        path="src/main.py",
        content="",
    )
    
    await db.create_node(node1)
    await db.create_node(node2)
    
    # Create edge
    edge = RepoEdge(
        id="edge-1",
        from_id="parent",
        to_id="child",
        relation=RelationType.CONTAINS,
    )
    
    await db.create_edge(edge)
    
    # Get edges
    edges = await db.get_edges("parent", direction="out")
    
    assert len(edges) == 1
    assert edges[0].to_id == "child"
    assert edges[0].relation == RelationType.CONTAINS


@pytest.mark.asyncio
async def test_get_neighbors(db):
    """Test getting neighboring nodes."""
    # Create nodes
    parent = RepoNode(id="parent", type=NodeType.DIRECTORY, path="src", content="")
    child1 = RepoNode(id="child1", type=NodeType.FILE, path="src/a.py", content="")
    child2 = RepoNode(id="child2", type=NodeType.FILE, path="src/b.py", content="")
    
    await db.create_node(parent)
    await db.create_node(child1)
    await db.create_node(child2)
    
    # Create edges
    await db.create_edge(RepoEdge(
        id="e1", from_id="parent", to_id="child1", relation=RelationType.CONTAINS
    ))
    await db.create_edge(RepoEdge(
        id="e2", from_id="parent", to_id="child2", relation=RelationType.CONTAINS
    ))
    
    # Get neighbors
    neighbors = await db.get_neighbors("parent")
    
    assert len(neighbors) == 2
    neighbor_ids = {n.id for n in neighbors}
    assert "child1" in neighbor_ids
    assert "child2" in neighbor_ids


@pytest.mark.asyncio
async def test_delete_node(db):
    """Test deleting a node."""
    node = RepoNode(
        id="to-delete",
        type=NodeType.FILE,
        path="temp.py",
        content="",
    )
    
    await db.create_node(node)
    assert await db.get_node("to-delete") is not None
    
    await db.delete_node("to-delete")
    assert await db.get_node("to-delete") is None


@pytest.mark.asyncio
async def test_health_check(db):
    """Test health check."""
    assert await db.health_check() is True
