"""Navigation API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ResolveRequest(BaseModel):
    """Request to resolve a repo:// URI."""
    uri: str


class ListRequest(BaseModel):
    """Request to list directory contents."""
    path: str
    repo: Optional[str] = None


@router.post("/resolve")
async def resolve_uri(request: ResolveRequest):
    """Resolve a repo:// URI to actual path and content."""
    # TODO: Implement
    return {
        "uri": request.uri,
        "resolved_path": None,
        "content": None,
        "message": "Not implemented yet"
    }


@router.post("/list")
async def list_directory(request: ListRequest):
    """List contents of a directory with metadata."""
    # TODO: Implement
    return {
        "path": request.path,
        "entries": [],
        "message": "Not implemented yet"
    }


@router.get("/context/{path:path}")
async def get_context_payload(path: str):
    """Get meta.yaml context payload for a path."""
    # TODO: Implement
    return {
        "path": path,
        "payload": None,
        "message": "Not implemented yet"
    }


@router.get("/repos")
async def list_repos():
    """List all indexed repositories."""
    # TODO: Implement
    return {
        "repos": [],
        "message": "Not implemented yet"
    }
