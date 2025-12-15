"""Server configuration loading."""

from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field


class StorageConfig(BaseModel):
    """Storage backend configuration."""
    
    # Graph backend: "neo4j" or "sqlite"
    graph_backend: str = "sqlite"
    graph_uri: str = "sqlite:///cip_graph.db"
    
    # Vector backend: "qdrant" or "chromadb"  
    vector_backend: str = "chromadb"
    vector_uri: str = "./chroma_data"
    
    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"


class LLMConfig(BaseModel):
    """LLM configuration for generation/scoring."""
    
    provider: str = "ollama"  # "ollama" or "openai"
    model: str = "llama3.2"
    base_url: str = "http://localhost:11434"
    api_key: Optional[str] = None


class WebhookConfig(BaseModel):
    """Webhook configuration."""
    
    enabled: bool = True
    github_secret: Optional[str] = None
    gitlab_token: Optional[str] = None


class ServerConfig(BaseModel):
    """Main server configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8420
    debug: bool = False
    
    storage: StorageConfig = Field(default_factory=StorageConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    webhook: WebhookConfig = Field(default_factory=WebhookConfig)
    
    # Repository paths to index
    repos: list[str] = Field(default_factory=list)


def load_config(config_path: Optional[Path] = None) -> ServerConfig:
    """Load configuration from YAML file or defaults."""
    if config_path and config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return ServerConfig(**data)
    return ServerConfig()
