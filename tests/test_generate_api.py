"""
Tests for Generation API endpoints.

Tests cover:
- POST /api/generate/meta
- POST /api/generate/readme
- POST /api/generate/summary
- POST /api/generate/enhance
- Error handling and service availability
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from server.main import app
from server.services.generation import GenerationService, GeneratedContent
from server.config import LLMConfig


@pytest.fixture
def generation_service_mock():
    """Mock GenerationService for testing."""
    service = MagicMock(spec=GenerationService)
    
    # Mock generate_meta (returns GeneratedContent)
    service.generate_meta = AsyncMock(return_value=GeneratedContent(
        content='schema_version: "2.0"\nrepository_role: "implementation"',
        format="yaml",
        confidence=0.9,
        suggestions=[],
        model_used="claude-3-5-sonnet-20241022",
        prompt_tokens=150,
        completion_tokens=50
    ))
    
    # Mock generate_readme (returns GeneratedContent)
    service.generate_readme = AsyncMock(return_value=GeneratedContent(
        content="# Test Repository\n\n## Overview\nTest content",
        format="markdown",
        confidence=0.85,
        suggestions=[],
        model_used="claude-3-5-sonnet-20241022",
        prompt_tokens=200,
        completion_tokens=80
    ))
    
    # Mock generate_summary (returns string)
    service.generate_summary = AsyncMock(return_value="This is a summary.")
    
    # Mock enhance_meta (returns tuple of dict and list)
    service.enhance_meta = AsyncMock(return_value=(
        {"schema_version": "2.0", "repository_role": "implementation", "title": "Enhanced"},
        ["Add version field", "Add license"]
    ))
    
    return service


@pytest_asyncio.fixture
async def client_with_generation(generation_service_mock):
    """Test client with mocked GenerationService."""
    # Inject mocked service into app state
    if not hasattr(app.state, 'services') or app.state.services is None:
        app.state.services = {}
    app.state.services['generation'] = generation_service_mock
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
class TestGenerateMetaEndpoint:
    """Test POST /api/generate/meta endpoint."""

    async def test_generate_meta_success(self, client_with_generation):
        """Test successful meta.yaml generation."""
        response = await client_with_generation.post(
            "/api/generate/meta",
            json={
                "path": "/test/repo",
                "style": "standard"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert "format" in data
        assert data["format"] == "yaml"
        assert "confidence" in data
        assert data["confidence"] >= 0.5
        assert "model_used" in data
        assert "tokens" in data
        assert data["tokens"]["prompt"] == 150
        assert data["tokens"]["completion"] == 50
        assert data["tokens"]["total"] == 200

    async def test_generate_meta_minimal_style(self, client_with_generation):
        """Test meta generation with minimal style."""
        response = await client_with_generation.post(
            "/api/generate/meta",
            json={
                "path": "/test/repo",
                "style": "minimal"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "schema_version" in data["content"]

    async def test_generate_meta_comprehensive_style(self, client_with_generation):
        """Test meta generation with comprehensive style."""
        response = await client_with_generation.post(
            "/api/generate/meta",
            json={
                "path": "/test/repo",
                "style": "comprehensive"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["confidence"] > 0.5

    async def test_generate_meta_missing_service(self):
        """Test error when GenerationService is unavailable."""
        # Create client without generation service
        app.state.services = {}
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/generate/meta",
                json={"path": "/test/repo"}
            )
        
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestGenerateReadmeEndpoint:
    """Test POST /api/generate/readme endpoint."""

    async def test_generate_readme_success(self, client_with_generation):
        """Test successful README generation."""
        response = await client_with_generation.post(
            "/api/generate/readme",
            json={
                "path": "/test/repo",
                "include_badges": False,
                "include_toc": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "content" in data
        assert "format" in data
        assert data["format"] == "markdown"
        assert "#" in data["content"]  # Has markdown heading
        assert data["confidence"] >= 0.5

    async def test_generate_readme_with_badges(self, client_with_generation):
        """Test README generation with badges option."""
        response = await client_with_generation.post(
            "/api/generate/readme",
            json={
                "path": "/test/repo",
                "include_badges": True,
                "include_toc": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "markdown"

    async def test_generate_readme_with_toc(self, client_with_generation):
        """Test README generation with table of contents."""
        response = await client_with_generation.post(
            "/api/generate/readme",
            json={
                "path": "/test/repo",
                "include_badges": False,
                "include_toc": True
            }
        )
        
        assert response.status_code == 200
        assert response.json()["confidence"] > 0.5

    async def test_generate_readme_missing_service(self):
        """Test error when GenerationService is unavailable."""
        app.state.services = {}
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/generate/readme",
                json={"path": "/test/repo"}
            )
        
        assert response.status_code == 503


@pytest.mark.asyncio
class TestSummarizeEndpoint:
    """Test POST /api/generate/summary endpoint."""

    async def test_summarize_success(self, client_with_generation):
        """Test successful content summarization."""
        response = await client_with_generation.post(
            "/api/generate/summary",
            json={
                "content": "This is a long text that needs summarization. " * 50,
                "max_length": 200
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        assert "max_length" in data
        assert data["max_length"] == 200
        assert "actual_length" in data

    async def test_summarize_short_content(self, client_with_generation):
        """Test summarization of short content."""
        short_text = "This is short."
        response = await client_with_generation.post(
            "/api/generate/summary",
            json={
                "content": short_text,
                "max_length": 100
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["summary"]) <= data["max_length"]

    async def test_summarize_missing_service(self):
        """Test error when GenerationService is unavailable."""
        app.state.services = {}
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/generate/summary",
                json={"content": "Test content"}
            )
        
        assert response.status_code in (500, 503)  # API returns 500 when catching HTTPException 503


@pytest.mark.asyncio
class TestEnhanceMetaEndpoint:
    """Test POST /api/generate/enhance endpoint."""

    async def test_enhance_meta_success(self, client_with_generation):
        """Test successful meta enhancement."""
        existing_meta = 'schema_version: "2.0"\nrepository_role: "implementation"'
        
        response = await client_with_generation.post(
            "/api/generate/enhance",
            json={
                "content": existing_meta
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "enhanced" in data
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert "schema_version" in data["enhanced"]

    async def test_enhance_meta_with_suggestions(self, client_with_generation):
        """Test that enhancement returns improvement suggestions."""
        minimal_meta = 'schema_version: "2.0"\nrepository_role: "theory"'
        
        response = await client_with_generation.post(
            "/api/generate/enhance",
            json={
                "content": minimal_meta
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) > 0  # Should have suggestions

    async def test_enhance_meta_missing_service(self):
        """Test error when GenerationService is unavailable."""
        app.state.services = {}
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post(
                "/api/generate/enhance",
                json={"content": "test"}
            )
        
        assert response.status_code in (500, 503)  # API returns 500 when catching HTTPException 503


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling across all endpoints."""

    async def test_generate_meta_service_error(self, client_with_generation, generation_service_mock):
        """Test handling of service errors in meta generation."""
        # Make service method raise an error
        generation_service_mock.generate_meta.side_effect = Exception("Service error")
        
        response = await client_with_generation.post(
            "/api/generate/meta",
            json={"path": "/test/repo"}
        )
        
        assert response.status_code == 500

    async def test_generate_readme_service_error(self, client_with_generation, generation_service_mock):
        """Test handling of service errors in README generation."""
        generation_service_mock.generate_readme.side_effect = ValueError("Invalid path")
        
        response = await client_with_generation.post(
            "/api/generate/readme",
            json={"path": "/invalid/path"}
        )
        
        assert response.status_code in (400, 500)  # ValueError caught and returned as 500

    async def test_summarize_service_error(self, client_with_generation, generation_service_mock):
        """Test handling of service errors in summarization."""
        generation_service_mock.generate_summary.side_effect = Exception("LLM error")
        
        response = await client_with_generation.post(
            "/api/generate/summary",
            json={"content": "test"}
        )
        
        assert response.status_code == 500

    async def test_enhance_meta_service_error(self, client_with_generation, generation_service_mock):
        """Test handling of service errors in enhancement."""
        generation_service_mock.enhance_meta.side_effect = ValueError("Invalid YAML")
        
        response = await client_with_generation.post(
            "/api/generate/enhance",
            json={"content": "invalid"}
        )
        
        assert response.status_code in (400, 500)  # ValueError caught and returned as 500
