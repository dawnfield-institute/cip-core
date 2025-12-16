"""
CIP Server - Main entry point.

Usage:
    python -m server.main
    uvicorn server.main:app --reload
    uvicorn main:app --reload (when in server directory)
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Handle both relative and absolute imports
try:
    from .config import load_config, ServerConfig
    from .api import register_routers
    from .webhook import router as webhook_router
    from .services import (
        KnowledgeGraphService,
        ValidationService,
        GenerationService,
        NavigationService,
        IndexingService,
    )
except ImportError:
    # Running as standalone script
    from config import load_config, ServerConfig
    from api import register_routers
    from webhook import router as webhook_router
    from services import (
        KnowledgeGraphService,
        ValidationService,
        GenerationService,
        NavigationService,
        IndexingService,
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("cip-server")

# Global state
config: ServerConfig = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    global config
    
    # Startup
    logger.info("Starting CIP Server...")
    config_path = Path("config/server.yaml")
    config = load_config(config_path if config_path.exists() else None)
    logger.info(f"Loaded config: storage={config.storage.graph_backend}/{config.storage.vector_backend}")
    
    # Initialize Kronos storage
    from kronos import KronosStorage
    storage = KronosStorage(
        graph_backend=config.storage.graph_backend,
        vector_backend=config.storage.vector_backend,
        graph_uri=config.storage.graph_uri,
        vector_uri=config.storage.vector_uri,
        embedding_model=config.storage.embedding_model,
        device="cpu",  # TODO: Detect CUDA availability
    )
    await storage.connect()
    logger.info("Kronos storage connected")
    
    # Initialize services and store in app.state
    app.state.services = {}
    app.state.services['graph'] = KnowledgeGraphService(storage)
    app.state.services['validation'] = ValidationService()
    app.state.services['generation'] = GenerationService(config.llm)
    app.state.services['navigation'] = NavigationService(repo_paths={})
    app.state.services['indexing'] = IndexingService(graph_service=app.state.services['graph'], storage=storage)
    
    # Start background workers
    await app.state.services['indexing'].start_worker()
    logger.info("All services initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CIP Server...")
    await app.state.services['indexing'].stop_worker()
    await storage.close()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="CIP Server",
    description="Unified CIP Infrastructure Server",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
register_routers(app)

# Register webhook routes
app.include_router(webhook_router, prefix="/webhook", tags=["webhooks"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not hasattr(app.state, 'services') or not app.state.services:
        return {"status": "starting", "version": "0.1.0"}
    
    # Check service health
    health = await app.state.services['graph'].storage.health_check()
    
    return {
        "status": "healthy" if all(health.values()) else "degraded",
        "version": "0.1.0",
        "storage": health,
        "services": {
            "graph": "ready",
            "validation": "ready",
            "generation": "ready",
            "navigation": "ready",
            "indexing": "ready",
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "CIP Server",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "graph": "/api/graph",
            "validate": "/api/validate",
            "generate": "/api/generate",
            "nav": "/api/nav",
            "score": "/api/score",
            "index": "/api/index",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8420)
