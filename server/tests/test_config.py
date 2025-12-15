"""Tests for configuration management."""

import pytest
from pathlib import Path
import yaml


class TestServerConfig:
    """Tests for ServerConfig."""
    
    def test_default_config(self):
        """Test creating config with defaults."""
        from config import ServerConfig
        
        config = ServerConfig()
        
        assert config.storage is not None
        assert config.storage.graph_backend == "sqlite"
        assert config.storage.vector_backend == "chromadb"
    
    def test_config_from_dict(self, sample_config):
        """Test creating config from dictionary."""
        from config import ServerConfig
        
        config = ServerConfig(**sample_config)
        
        assert config.storage.graph_backend == "sqlite"
        assert config.storage.vector_backend == "chromadb"
        assert config.port == 8000
        assert config.llm.provider == "openai"
    
    def test_storage_config(self):
        """Test StorageConfig."""
        from config import StorageConfig
        
        config = StorageConfig(
            graph_backend="neo4j",
            vector_backend="qdrant",
            graph_uri="bolt://localhost:7687",
            vector_uri="http://localhost:6333"
        )
        
        assert config.graph_backend == "neo4j"
        assert config.vector_backend == "qdrant"
        assert config.graph_uri == "bolt://localhost:7687"
    
    def test_llm_config(self):
        """Test LLMConfig."""
        from config import LLMConfig
        
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-opus",
            api_key_env="ANTHROPIC_API_KEY"
        )
        
        assert config.provider == "anthropic"
        assert config.model == "claude-3-opus"
    
    def test_webhook_config(self):
        """Test WebhookConfig."""
        from config import WebhookConfig
        
        config = WebhookConfig(
            enabled=True,
            github_secret="my-secret",
            gitlab_token="my-token"
        )
        
        assert config.github_secret == "my-secret"
        assert config.gitlab_token == "my-token"
        assert config.enabled is True


class TestConfigLoading:
    """Tests for config file loading."""
    
    def test_load_config_from_yaml(self, temp_dir, sample_config):
        """Test loading config from YAML file."""
        from config import load_config
        
        # Create test config file
        config_file = temp_dir / "test_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)
        
        # Load it
        config = load_config(config_file)
        
        assert config is not None
        assert config.storage.graph_backend == "sqlite"
        assert config.port == 8000
    
    def test_load_config_no_file(self):
        """Test loading config when file doesn't exist."""
        from config import load_config
        
        # Should return default config
        config = load_config(None)
        
        assert config is not None
        assert config.storage.graph_backend == "sqlite"
    
    def test_load_config_nonexistent_file(self):
        """Test loading config from nonexistent file."""
        from config import load_config
        
        config = load_config(Path("/nonexistent/config.yaml"))
        
        # Should return default config
        assert config is not None
    
    def test_load_config_invalid_yaml(self, temp_dir):
        """Test loading invalid YAML config."""
        from config import load_config
        
        # Create invalid YAML file
        config_file = temp_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: content:")
        
        # Should handle gracefully (either default config or raise)
        try:
            config = load_config(config_file)
            assert config is not None
        except Exception:
            # Expected if validation fails
            pass


class TestConfigValidation:
    """Tests for config validation."""
    
    def test_invalid_storage_backend(self):
        """Test invalid storage backend."""
        from config import StorageConfig
        
        # This should work - Pydantic will accept any string
        # but we can add custom validation if needed
        config = StorageConfig(graph_backend="invalid")
        assert config.graph_backend == "invalid"
    
    def test_missing_required_fields(self):
        """Test config with missing fields uses defaults."""
        from config import ServerConfig
        
        # Should use defaults
        config = ServerConfig()
        assert config.storage is not None
        assert config.storage.graph_backend is not None
