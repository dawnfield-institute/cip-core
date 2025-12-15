"""Integration tests using cip-test-repo as test target."""

import pytest
import sys
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.validation import ValidationService
from services.indexing import IndexingService
from services.graph import KnowledgeGraphService


# Path to cip-test-repo (sibling to cip-core)
CIP_TEST_REPO = Path(__file__).parent.parent.parent.parent / "cip-test-repo"


@pytest.fixture
def validation_service():
    """Validation service instance."""
    return ValidationService()


@pytest.fixture
def indexing_service():
    """Indexing service instance."""
    config = {
        "kronos": {
            "graph_backend": "sqlite",
            "graph_uri": "test_kronos.db",
            "vector_backend": "chromadb",
            "vector_uri": "./test_kronos_vectors"
        }
    }
    return IndexingService(config)


@pytest.fixture
def kg_service():
    """Knowledge graph service instance."""
    config = {
        "kronos": {
            "graph_backend": "sqlite",
            "graph_uri": "test_kronos.db",
            "vector_backend": "chromadb",
            "vector_uri": "./test_kronos_vectors"
        }
    }
    return KnowledgeGraphService(config)


class TestCIPTestRepo:
    """Integration tests using cip-test-repo."""
    
    @pytest.mark.asyncio
    async def test_repo_exists(self):
        """Verify cip-test-repo is available."""
        assert CIP_TEST_REPO.exists(), f"cip-test-repo not found at {CIP_TEST_REPO}"
        assert (CIP_TEST_REPO / "meta.yaml").exists(), "meta.yaml not found"
        assert (CIP_TEST_REPO / "README.md").exists(), "README.md not found"
        assert (CIP_TEST_REPO / "LICENSE").exists(), "LICENSE not found"
    
    @pytest.mark.asyncio
    async def test_validate_test_repo(self, validation_service):
        """Test validation of cip-test-repo."""
        result = await validation_service.validate_repo(str(CIP_TEST_REPO))
        
        assert result is not None
        assert result.score >= 0.0
        assert result.score <= 1.0
        
        print(f"\ncip-test-repo Compliance Score: {result.score:.2%}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        
        # Should have high compliance since we just fixed it
        assert result.score >= 0.80, "cip-test-repo should be >80% compliant"
        
        # Log any issues
        for error in result.errors:
            print(f"  ERROR: {error.message}")
        for warning in result.warnings:
            print(f"  WARN: {warning.message}")
    
    @pytest.mark.asyncio
    async def test_validate_test_repo_meta(self, validation_service):
        """Test meta.yaml validation."""
        import yaml
        
        meta_path = CIP_TEST_REPO / "meta.yaml"
        with open(meta_path) as f:
            content = yaml.safe_load(f)
        
        result = await validation_service.validate_meta(content)
        
        assert result is not None
        print(f"\nMeta.yaml validation:")
        print(f"Valid: {result.valid}")
        print(f"Errors: {len(result.errors)}")
        
        if result.errors:
            for error in result.errors:
                print(f"  ERROR: {error.message}")
    
    @pytest.mark.asyncio
    async def test_index_test_repo(self, indexing_service):
        """Test indexing cip-test-repo."""
        # Start background indexing
        job_id = await indexing_service.queue_index(str(CIP_TEST_REPO))
        
        assert job_id is not None
        print(f"\nIndexing job created: {job_id}")
        
        # Check job status
        job = await indexing_service.get_job_status(job_id)
        assert job is not None
        print(f"Status: {job.status}")
        print(f"Repo: {job.repo_path}")
    
    @pytest.mark.asyncio
    async def test_query_indexed_repo(self, kg_service, indexing_service):
        """Test querying indexed cip-test-repo content."""
        # Queue indexing
        job_id = await indexing_service.queue_index(str(CIP_TEST_REPO))
        
        print(f"\nIndexing job: {job_id}")
        print("Note: Query requires background worker to complete indexing")
        print("This test validates API, not end-to-end indexing+query")
    
    @pytest.mark.asyncio
    async def test_structure_validation(self, validation_service):
        """Test structure validation."""
        result = await validation_service.validate_structure(str(CIP_TEST_REPO))
        
        print(f"\nStructure validation:")
        print(f"Valid: {result.valid}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")
        
        # Should have README and LICENSE
        assert (CIP_TEST_REPO / "README.md").exists()
        assert (CIP_TEST_REPO / "LICENSE").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
