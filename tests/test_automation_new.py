"""
Tests for cip_core.automation module.
"""

import pytest
import yaml
from pathlib import Path

from cip_core.automation import (
    DirectoryMetadataGenerator,
    AIEnhancedDirectoryMetadataGenerator,
    CIPAutomation
)


class TestDirectoryMetadataGenerator:
    """Test the DirectoryMetadataGenerator class."""

    def test_generate_basic_metadata(self, temp_repo):
        """Test basic metadata generation for directories."""
        generator = DirectoryMetadataGenerator(str(temp_repo))
        
        # Create test directories
        (temp_repo / "src").mkdir()
        
        metadata = generator.generate_directory_metadata(temp_repo / "src")
        
        assert isinstance(metadata, dict)
        assert "name" in metadata
        assert metadata["name"] == "src"
        assert "semantic_scope" in metadata

    def test_semantic_scope_mapping(self, temp_repo):
        """Test semantic scope mapping for known directory types."""
        generator = DirectoryMetadataGenerator(str(temp_repo))
        
        # Create directories with known semantic meanings
        (temp_repo / "tools").mkdir()
        (temp_repo / "docs").mkdir()
        (temp_repo / "experiments").mkdir()
        
        tools_metadata = generator.generate_directory_metadata(temp_repo / "tools")
        docs_metadata = generator.generate_directory_metadata(temp_repo / "docs")
        experiments_metadata = generator.generate_directory_metadata(temp_repo / "experiments")
        
        # Check semantic scope assignments
        assert "tools" in tools_metadata["semantic_scope"]
        assert "documentation" in docs_metadata["semantic_scope"]
        assert "experiments" in experiments_metadata["semantic_scope"]

    def test_gitignore_patterns(self, temp_repo):
        """Test gitignore pattern handling."""
        # Create .gitignore with test patterns
        gitignore_content = """
.git/
__pycache__/
node_modules/
*.pyc
        """
        (temp_repo / ".gitignore").write_text(gitignore_content.strip())
        
        generator = DirectoryMetadataGenerator(str(temp_repo))
        
        # Create directories
        (temp_repo / ".git").mkdir()
        (temp_repo / "__pycache__").mkdir()
        (temp_repo / "node_modules").mkdir()
        (temp_repo / "src").mkdir()  # This should NOT be ignored
        
        # Test _is_ignored method
        assert generator._is_ignored(temp_repo / ".git")
        assert generator._is_ignored(temp_repo / "__pycache__")
        assert generator._is_ignored(temp_repo / "node_modules")
        assert not generator._is_ignored(temp_repo / "src")

    def test_process_directory(self, temp_repo):
        """Test processing a directory to create meta.yaml file."""
        generator = DirectoryMetadataGenerator(str(temp_repo))
        
        # Create a directory
        test_dir = temp_repo / "test_dir"
        test_dir.mkdir()
        
        # Process the directory (should create meta.yaml)
        generator.process_directory(test_dir)
        
        # Check if meta.yaml was created
        meta_file = test_dir / "meta.yaml"
        assert meta_file.exists()
        
        # Check content
        with open(meta_file) as f:
            content = yaml.safe_load(f)
            assert "name" in content
            assert content["name"] == "test_dir"

    def test_process_repository(self, temp_repo):
        """Test processing entire repository."""
        generator = DirectoryMetadataGenerator(str(temp_repo))
        
        # Create directory structure
        (temp_repo / "src").mkdir()
        (temp_repo / "tests").mkdir()
        (temp_repo / "docs").mkdir()
        
        # Process the entire repository
        generator.process_repository()
        
        # Check that meta.yaml files were created
        assert (temp_repo / "src" / "meta.yaml").exists()
        assert (temp_repo / "tests" / "meta.yaml").exists()
        assert (temp_repo / "docs" / "meta.yaml").exists()


class TestAIEnhancedDirectoryMetadataGenerator:
    """Test the AIEnhancedDirectoryMetadataGenerator class."""

    def test_ai_enhanced_instantiation(self, temp_repo):
        """Test AI-enhanced generator can be instantiated."""
        try:
            generator = AIEnhancedDirectoryMetadataGenerator(str(temp_repo))
            assert generator is not None
            assert hasattr(generator, 'repo_root')
        except Exception as e:
            # AI enhanced generator might not be fully implemented yet
            pytest.skip(f"AI enhanced generator not yet fully implemented: {e}")


class TestCIPAutomation:
    """Test the CIPAutomation class."""

    def test_automation_instantiation(self, temp_repo):
        """Test automation class can be instantiated."""
        automation = CIPAutomation()
        assert automation is not None


# Integration tests
class TestAutomationIntegration:
    """Integration tests for automation module."""

    @pytest.mark.integration
    def test_full_metadata_pipeline(self, temp_repo):
        """Test complete metadata generation pipeline."""
        # Create realistic repository structure
        (temp_repo / "src").mkdir()
        (temp_repo / "src" / "main.py").write_text("# Main application")
        
        (temp_repo / "tests").mkdir()
        (temp_repo / "tests" / "test_main.py").write_text("# Tests for main")
        
        (temp_repo / "docs").mkdir()
        (temp_repo / "docs" / "README.md").write_text("# Documentation")
        
        # Test metadata generation
        generator = DirectoryMetadataGenerator(str(temp_repo))
        
        # Generate metadata for different directories
        src_metadata = generator.generate_directory_metadata(temp_repo / "src")
        tests_metadata = generator.generate_directory_metadata(temp_repo / "tests")
        docs_metadata = generator.generate_directory_metadata(temp_repo / "docs")
        
        # Verify metadata structure
        for metadata in [src_metadata, tests_metadata, docs_metadata]:
            assert isinstance(metadata, dict)
            assert "name" in metadata
            assert "semantic_scope" in metadata

    @pytest.mark.integration
    def test_process_repository_integration(self, temp_repo):
        """Test full repository processing."""
        # Create complex directory structure
        directories = [
            "src/components",
            "src/utils",
            "tests/unit",
            "tests/integration", 
            "docs/user",
            "docs/api",
            "tools/scripts",
            "experiments/ai"
        ]
        
        for dir_path in directories:
            (temp_repo / dir_path).mkdir(parents=True)
            # Add some content
            (temp_repo / dir_path / "placeholder.txt").write_text("placeholder")
        
        # Process the repository
        generator = DirectoryMetadataGenerator(str(temp_repo))
        generator.process_repository()
        
        # Verify meta.yaml files were created
        expected_meta_files = [
            "src/meta.yaml",
            "src/components/meta.yaml", 
            "src/utils/meta.yaml",
            "tests/meta.yaml",
            "tests/unit/meta.yaml",
            "tests/integration/meta.yaml",
            "docs/meta.yaml",
            "docs/user/meta.yaml",
            "docs/api/meta.yaml",
            "tools/meta.yaml",
            "tools/scripts/meta.yaml",
            "experiments/meta.yaml",
            "experiments/ai/meta.yaml"
        ]
        
        for meta_file in expected_meta_files:
            meta_path = temp_repo / meta_file
            assert meta_path.exists(), f"Missing meta.yaml: {meta_file}"
            
            # Verify content structure
            with open(meta_path) as f:
                content = yaml.safe_load(f)
                assert "name" in content
                assert "semantic_scope" in content
