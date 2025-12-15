"""Indexing API endpoints."""

from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class IndexRequest(BaseModel):
    """Request to index a repository."""
    path: str
    force: bool = False  # Force full reindex


class SyncStatus(BaseModel):
    """Repository sync status."""
    repo: str
    last_sync: Optional[str] = None
    status: str = "unknown"
    nodes_count: int = 0
    edges_count: int = 0


@router.post("/repo")
async def index_repo(request_body: IndexRequest, request: Request):
    """Index or reindex a repository."""
    services = request.app.state.services
    indexing_service = services.get("indexing")
    
    if not indexing_service:
        raise HTTPException(status_code=503, detail="Indexing service not available")
    
    job_id = await indexing_service.queue_index(request_body.path, request_body.force)
    
    return {
        "path": request_body.path,
        "status": "queued",
        "job_id": job_id
    }


@router.get("/status/{repo}")
async def get_sync_status(repo: str, request: Request):
    """Get sync status for a repository."""
    services = request.app.state.services
    indexing_service = services.get("indexing")
    
    if not indexing_service:
        raise HTTPException(status_code=503, detail="Indexing service not available")
    
    status = await indexing_service.get_sync_status(repo)
    
    return {
        "repo": status.repo,
        "last_sync": status.last_sync.isoformat() if status.last_sync else None,
        "status": status.status,
        "nodes_count": status.nodes_count,
        "edges_count": status.edges_count
    }


@router.post("/sync/{repo}")
async def force_sync(repo: str, request: Request):
    """Force sync a repository (git pull + reindex)."""
    services = request.app.state.services
    indexing_service = services.get("indexing")
    
    if not indexing_service:
        raise HTTPException(status_code=503, detail="Indexing service not available")
    
    job_id = await indexing_service.force_sync(repo)
    
    return {
        "repo": repo,
        "status": "queued",
        "job_id": job_id
    }


@router.delete("/repo/{repo}")
async def remove_repo(repo: str, request: Request):
    """Remove a repository from the index."""
    services = request.app.state.services
    indexing_service = services.get("indexing")
    
    if not indexing_service:
        raise HTTPException(status_code=503, detail="Indexing service not available")
    
    removed = await indexing_service.remove_repo(repo)
    
    return {
        "repo": repo,
        "removed": removed
    }


@router.get("/queue")
async def get_queue_status(request: Request):
    """Get status of indexing queue."""
    services = request.app.state.services
    indexing_service = services.get("indexing")
    
    if not indexing_service:
        raise HTTPException(status_code=503, detail="Indexing service not available")
    
    stats = indexing_service.get_queue_stats()
    
    return stats
