"""Integration tests for end-to-end workflows."""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import AsyncMock


@pytest.mark.asyncio
@pytest.mark.integration
class TestIndexingIntegration:
    """Integration tests for indexing workflow."""
    
    async def test_index_small_repo(self, mock_storage, temp_dir):
        """Test indexing a small test repository."""
        from services import KnowledgeGraphService, IndexingService
        
        # Create test repository structure
        repo_dir = temp_dir / "test-repo"
        repo_dir.mkdir()
        
        # Add Python file
        (repo_dir / "main.py").write_text('''
"""Main module."""

def hello_world():
    """Say hello."""
    print("Hello, World!")

class TestClass:
    """A test class."""
    pass
''')
        
        # Add Markdown file
        (repo_dir / "README.md").write_text('''
# Test Repository

This is a test.

## Section 1

Content here.
''')
        
        # Add meta.yaml
        (repo_dir / "meta.yaml").write_text('''
schema_version: "3.0"
description: "Test repo"
''')
        
        # Create services
        graph_service = KnowledgeGraphService(mock_storage)
        indexing_service = IndexingService(
            graph_service=graph_service,
            storage=mock_storage
        )
        
        # Queue indexing
        job_id = await indexing_service.queue_index(str(repo_dir))
        
        assert job_id is not None
        
        # Get job
        job = await indexing_service.get_job_status(job_id)
        assert job is not None
        assert job.status == "pending"
        
        # Process job manually (not via background worker)
        job.status = "running"
        try:
            await indexing_service._index_repository(job)
            job.status = "completed"
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
        
        # Check results
        sync_status = await indexing_service.get_sync_status(repo_dir.name)
        assert sync_status is not None
        assert sync_status.nodes_count > 0
        
        # Verify storage calls
        assert mock_storage.store_node.called
    
    async def test_skip_ignored_files(self, mock_storage, temp_dir):
        """Test that ignored files are skipped."""
        from services import KnowledgeGraphService, IndexingService
        
        # Create test repository with ignored directories
        repo_dir = temp_dir / "test-repo"
        repo_dir.mkdir()
        (repo_dir / "__pycache__").mkdir()
        (repo_dir / "__pycache__" / "test.pyc").write_text("bytecode")
        (repo_dir / "main.py").write_text("def test(): pass")
        
        graph_service = KnowledgeGraphService(mock_storage)
        indexing_service = IndexingService(
            graph_service=graph_service,
            storage=mock_storage
        )
        
        job_id = await indexing_service.queue_index(str(repo_dir))
        job = await indexing_service.get_job_status(job_id)
        
        job.status = "running"
        await indexing_service._index_repository(job)
        
        # Should only index main.py, not __pycache__ files
        calls = [call for call in mock_storage.store_node.call_args_list]
        paths = [call[1].get('path', '') for call in calls if len(call) > 1]
        
        # Check no __pycache__ files were indexed
        assert not any("__pycache__" in str(path) for path in paths)


@pytest.mark.asyncio
@pytest.mark.integration
class TestQueryIntegration:
    """Integration tests for query workflow."""
    
    async def test_query_after_indexing(self, mock_storage):
        """Test querying after indexing."""
        from services import KnowledgeGraphService
        
        # Mock query results
        mock_storage.query = AsyncMock(return_value=[
            {
                "id": "node_1",
                "type": "function",
                "path": "main.py#hello",
                "content": "def hello():",
                "metadata": {},
                "score": 0.95
            }
        ])
        
        service = KnowledgeGraphService(mock_storage)
        results = await service.query("hello function", limit=10)
        
        assert len(results) > 0
        assert results[0]["type"] == "function"
        assert "hello" in results[0]["path"]


@pytest.mark.asyncio
@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""
    
    async def test_full_workflow(self, mock_storage, temp_dir):
        """Test complete workflow: index → query → get node."""
        from services import KnowledgeGraphService, IndexingService
        
        # Setup
        repo_dir = temp_dir / "test-repo"
        repo_dir.mkdir()
        (repo_dir / "code.py").write_text('''
def my_function():
    """My function."""
    pass
''')
        
        graph_service = KnowledgeGraphService(mock_storage)
        indexing_service = IndexingService(
            graph_service=graph_service,
            storage=mock_storage
        )
        
        # 1. Index
        job_id = await indexing_service.queue_index(str(repo_dir))
        job = await indexing_service.get_job_status(job_id)
        job.status = "running"
        
        try:
            await indexing_service._index_repository(job)
            job.status = "completed"
        except Exception as e:
            pytest.fail(f"Indexing failed: {e}")
        
        # 2. Query
        results = await graph_service.query("my_function")
        assert isinstance(results, list)
        
        # 3. Get specific node
        if results and len(results) > 0:
            node_id = results[0].get("id")
            if node_id:
                node = await graph_service.get_node(node_id)
                assert node is not None
