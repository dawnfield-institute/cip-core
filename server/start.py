#!/usr/bin/env python3
"""
Quick start script for CIP Server.

This script:
1. Checks dependencies
2. Creates default config if needed
3. Starts the server

Usage:
    python start.py
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import kronos
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall dependencies with:")
        print("  pip install -r requirements.txt")
        return False


def create_default_config():
    """Create default config if it doesn't exist."""
    config_dir = Path("config")
    config_file = config_dir / "server.yaml"
    
    if config_file.exists():
        print(f"✓ Config found: {config_file}")
        return
    
    if not config_dir.exists():
        print(f"Creating config directory: {config_dir}")
        config_dir.mkdir(parents=True)
    
    # Create minimal config
    minimal_config = """# CIP Server Configuration
# This is a minimal config using SQLite + ChromaDB (no Docker needed)

storage:
  graph_backend: "sqlite"
  vector_backend: "chromadb"
  sqlite_path: "./data/cip.db"
  chromadb_path: "./data/chromadb"
  embedding_model: "all-MiniLM-L6-v2"
  embedding_dimension: 384

server:
  host: "0.0.0.0"
  port: 8000
  workers: 1

llm:
  provider: "openai"
  model: "gpt-4"
  api_key_env: "OPENAI_API_KEY"

webhook:
  secret: "change-me-in-production"
  github_enabled: true
  gitlab_enabled: false
  bitbucket_enabled: false
"""
    
    config_file.write_text(minimal_config)
    print(f"✓ Created default config: {config_file}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("CIP Server - Quick Start")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✓ All dependencies installed")
    print()
    
    # Create config
    print("Checking configuration...")
    create_default_config()
    print()
    
    # Start server
    print("Starting server...")
    print()
    print("Server will be available at:")
    print("  - API: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("  - Health: http://localhost:8000/health")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")


if __name__ == "__main__":
    main()
