"""API routers package."""

from fastapi import APIRouter

# Main API router
api_router = APIRouter(prefix="/api")


def register_routers(app):
    """Register all API routers with the app."""
    from . import graph, validate, generate, nav, score, index
    
    api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
    api_router.include_router(validate.router, prefix="/validate", tags=["validation"])
    api_router.include_router(generate.router, prefix="/generate", tags=["generation"])
    api_router.include_router(nav.router, prefix="/nav", tags=["navigation"])
    api_router.include_router(score.router, prefix="/score", tags=["scoring"])
    api_router.include_router(index.router, prefix="/index", tags=["indexing"])
    
    app.include_router(api_router)
