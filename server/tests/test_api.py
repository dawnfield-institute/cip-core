"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def test_app(mock_storage):
    """Create a test FastAPI app."""
    from fastapi import FastAPI
    from api import register_routers
    from services import KnowledgeGraphService, IndexingService
    
    app = FastAPI()
    
    # Mock services
    app.state.services = {}
    app.state.services['graph'] = KnowledgeGraphService(mock_storage)
    app.state.services['indexing'] = IndexingService(
        graph_service=app.state.services['graph'],
        storage=mock_storage
    )
    app.state.services['validation'] = MagicMock()
    app.state.services['navigation'] = MagicMock()
    app.state.services['scoring'] = MagicMock()
    
    register_routers(app)
    
    return app


class TestGraphAPI:
    """Tests for Graph API endpoints."""
    
    def test_query_endpoint(self, test_app, mock_storage):
        """Test POST /api/graph/query."""
        client = TestClient(test_app)
        
        response = client.post(
            "/api/graph/query",
            json={"query": "test query", "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert data["query"] == "test query"
    
    def test_get_node_endpoint(self, test_app, mock_storage):
        """Test GET /api/graph/node/{id}."""
        client = TestClient(test_app)
        
        response = client.get("/api/graph/node/node_123")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
    
    def test_get_node_not_found(self, test_app, mock_storage):
        """Test GET /api/graph/node/{id} with non-existent node."""
        client = TestClient(test_app)
        
        # Mock storage to return None
        mock_storage.get_node = AsyncMock(return_value=None)
        
        response = client.get("/api/graph/node/nonexistent")
        
        assert response.status_code == 404
    
    def test_trace_concept_endpoint(self, test_app, mock_storage):
        """Test GET /api/graph/trace/{concept}."""
        client = TestClient(test_app)
        
        response = client.get("/api/graph/trace/MyClass")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "concept" in data
    
    def test_find_related_endpoint(self, test_app, mock_storage):
        """Test GET /api/graph/related/{id}."""
        client = TestClient(test_app)
        
        response = client.get("/api/graph/related/node_123")
        
        assert response.status_code == 200
        data = response.json()
        assert "related" in data
        assert "node_id" in data


class TestIndexAPI:
    """Tests for Index API endpoints."""
    
    def test_index_repo_endpoint(self, test_app, mock_storage):
        """Test POST /api/index/repo."""
        client = TestClient(test_app)
        
        response = client.post(
            "/api/index/repo",
            json={"path": "/path/to/repo", "force": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
    
    def test_get_sync_status_endpoint(self, test_app, mock_storage):
        """Test GET /api/index/status/{repo}."""
        client = TestClient(test_app)
        
        response = client.get("/api/index/status/test-repo")
        
        assert response.status_code == 200
        data = response.json()
        assert "repo" in data
        assert "status" in data
    
    def test_force_sync_endpoint(self, test_app, mock_storage):
        """Test POST /api/index/sync/{repo}."""
        client = TestClient(test_app)
        
        response = client.post("/api/index/sync/test-repo")
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
    
    def test_remove_repo_endpoint(self, test_app, mock_storage):
        """Test DELETE /api/index/repo/{repo}."""
        client = TestClient(test_app)
        
        response = client.delete("/api/index/repo/test-repo")
        
        assert response.status_code == 200
        data = response.json()
        assert "removed" in data
    
    def test_get_queue_endpoint(self, test_app, mock_storage):
        """Test GET /api/index/queue."""
        client = TestClient(test_app)
        
        response = client.get("/api/index/queue")
        
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert "running" in data
        assert "completed" in data
        assert "failed" in data


class TestServiceUnavailable:
    """Tests for service unavailability handling."""
    
    def test_graph_service_unavailable(self):
        """Test API behavior when graph service is unavailable."""
        from fastapi import FastAPI
        from api import register_routers
        
        app = FastAPI()
        app.state.services = {}  # No services
        register_routers(app)
        
        client = TestClient(app)
        response = client.post(
            "/api/graph/query",
            json={"query": "test"}
        )
        
        assert response.status_code == 503
    
    def test_indexing_service_unavailable(self):
        """Test API behavior when indexing service is unavailable."""
        from fastapi import FastAPI
        from api import register_routers
        
        app = FastAPI()
        app.state.services = {}  # No services
        register_routers(app)
        
        client = TestClient(app)
        response = client.post(
            "/api/index/repo",
            json={"path": "/test"}
        )
        
        assert response.status_code == 503
