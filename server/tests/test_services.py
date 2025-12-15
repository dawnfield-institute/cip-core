"""Tests for service layer."""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock


class TestKnowledgeGraphService:
    """Tests for KnowledgeGraphService."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_storage):
        """Test service initialization."""
        from services import KnowledgeGraphService
        
        service = KnowledgeGraphService(mock_storage)
        assert service.storage == mock_storage
    
    @pytest.mark.asyncio
    async def test_query(self, mock_storage):
        """Test semantic query."""
        from services import KnowledgeGraphService
        
        service = KnowledgeGraphService(mock_storage)
        results = await service.query("test query", limit=5)
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert "id" in results[0]
        assert "type" in results[0]
        mock_storage.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_node(self, mock_storage):
        """Test getting a specific node."""
        from services import KnowledgeGraphService
        
        service = KnowledgeGraphService(mock_storage)
        node = await service.get_node("node_123")
        
        assert node is not None
        assert "id" in node
        mock_storage.get_node.assert_called_once_with("node_123")
    
    @pytest.mark.asyncio
    async def test_get_node_not_found(self, mock_storage):
        """Test getting a non-existent node."""
        from services import KnowledgeGraphService
        
        mock_storage.get_node = AsyncMock(return_value=None)
        service = KnowledgeGraphService(mock_storage)
        node = await service.get_node("nonexistent")
        
        assert node is None
    
    @pytest.mark.asyncio
    async def test_trace_concept(self, mock_storage):
        """Test tracing concept evolution."""
        from services import KnowledgeGraphService
        
        service = KnowledgeGraphService(mock_storage)
        history = await service.trace_concept("MyClass")
        
        assert isinstance(history, list)
    
    @pytest.mark.asyncio
    async def test_find_related(self, mock_storage):
        """Test finding related nodes."""
        from services import KnowledgeGraphService
        
        service = KnowledgeGraphService(mock_storage)
        related = await service.find_related("node_123")
        
        assert isinstance(related, list)


class TestIndexingService:
    """Tests for IndexingService."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_storage):
        """Test service initialization."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        assert service.storage == mock_storage
        assert service.graph_service == graph_service
        assert len(service.job_queue) == 0
    
    @pytest.mark.asyncio
    async def test_queue_index(self, mock_storage):
        """Test queuing an indexing job."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        job_id = await service.queue_index("/path/to/repo", force=False)
        
        assert job_id is not None
        assert len(service.job_queue) == 1
        assert service.job_queue[0].repo_path == "/path/to/repo"
        assert service.job_queue[0].force is False
    
    @pytest.mark.asyncio
    async def test_get_job_status(self, mock_storage):
        """Test getting job status."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        job_id = await service.queue_index("/path/to/repo")
        status = await service.get_job_status(job_id)
        
        assert status is not None
        assert status.id == job_id
        assert status.status == "pending"
    
    @pytest.mark.asyncio
    async def test_get_sync_status(self, mock_storage):
        """Test getting sync status."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        status = await service.get_sync_status("test-repo")
        
        assert status is not None
        assert status.repo == "test-repo"
    
    @pytest.mark.asyncio
    async def test_force_sync(self, mock_storage):
        """Test force sync."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        job_id = await service.force_sync("/path/to/repo")
        
        assert job_id is not None
        assert len(service.job_queue) == 1
        assert service.job_queue[0].force is True
    
    @pytest.mark.asyncio
    async def test_remove_repo(self, mock_storage):
        """Test removing a repository."""
        from services import IndexingService, KnowledgeGraphService, SyncStatus
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        # Add a repo to status
        service.sync_status["test-repo"] = SyncStatus(repo="test-repo")
        
        # Remove it
        result = await service.remove_repo("test-repo")
        
        assert result is True
        assert "test-repo" not in service.sync_status
    
    def test_get_queue_stats(self, mock_storage):
        """Test getting queue statistics."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        stats = service.get_queue_stats()
        
        assert "pending" in stats
        assert "running" in stats
        assert "completed" in stats
        assert "failed" in stats
        assert stats["pending"] == 0
    
    def test_should_skip(self, mock_storage):
        """Test skip pattern matching."""
        from services import IndexingService, KnowledgeGraphService
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        assert service._should_skip("__pycache__/test.py")
        assert service._should_skip(".git/config")
        assert service._should_skip("node_modules/package.json")
        assert service._should_skip("venv/lib/python")
        assert not service._should_skip("src/main.py")
        assert not service._should_skip("tests/test_file.py")
    
    def test_map_entity_type(self, mock_storage):
        """Test entity type mapping."""
        from services import IndexingService, KnowledgeGraphService
        from kronos.types import NodeType
        
        graph_service = KnowledgeGraphService(mock_storage)
        service = IndexingService(graph_service=graph_service, storage=mock_storage)
        
        assert service._map_entity_type("function") == NodeType.FUNCTION
        assert service._map_entity_type("method") == NodeType.METHOD
        assert service._map_entity_type("class") == NodeType.CLASS
        assert service._map_entity_type("section") == NodeType.SECTION
        assert service._map_entity_type("unknown") == NodeType.FILE


class TestValidationService:
    """Tests for ValidationService."""
    
    def test_initialization(self):
        """Test service initialization."""
        from services import ValidationService
        
        service = ValidationService()
        assert service is not None


class TestNavigationService:
    """Tests for NavigationService."""
    
    def test_initialization(self):
        """Test service initialization."""
        from services import NavigationService
        
        service = NavigationService(repo_paths={})
        assert service is not None
        assert service.repo_paths == {}
    
    def test_initialization_with_repos(self):
        """Test service initialization with repositories."""
        from services import NavigationService
        
        repos = {"repo1": "/path/to/repo1", "repo2": "/path/to/repo2"}
        service = NavigationService(repo_paths=repos)
        
        assert service.repo_paths == repos


class TestScoringService:
    """Tests for ScoringService."""
    
    def test_initialization(self):
        """Test service initialization."""
        from services import ScoringService
        
        service = ScoringService()
        assert service is not None
