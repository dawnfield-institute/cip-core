"""Knowledge Graph API endpoints."""

from fastapi import APIRouter, Query, Request, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class QueryRequest(BaseModel):
    """Semantic query request."""
    query: str
    repo: Optional[str] = None
    limit: int = 10
    include_context: bool = True


class QueryResult(BaseModel):
    """Query result item."""
    id: str
    type: str
    path: str
    content: str
    score: float
    relationships: list[dict] = []


@router.post("/query")
async def query_repo(request_body: QueryRequest, request: Request):
    """Semantic search across repository knowledge graph."""
    services = request.app.state.services
    graph_service = services.get("graph")
    
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    results = await graph_service.query(
        request_body.query,
        limit=request_body.limit,
        expand_graph=request_body.include_context
    )
    
    return {
        "query": request_body.query,
        "results": results,
        "count": len(results)
    }


@router.get("/node/{node_id}")
async def get_node(node_id: str, request: Request):
    """Get a specific node by ID."""
    services = request.app.state.services
    graph_service = services.get("graph")
    
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    node = await graph_service.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    return node


@router.get("/trace/{concept}")
async def trace_concept(
    concept: str,
    depth: int = Query(default=5, ge=1, le=20),
    request: Request = None
):
    """Trace temporal evolution of a concept."""
    services = request.app.state.services
    graph_service = services.get("graph")
    
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    history = await graph_service.trace_concept(concept)
    
    return {
        "concept": concept,
        "history": history,
        "count": len(history)
    }


@router.get("/related/{node_id}")
async def find_related(
    node_id: str,
    relationship_type: Optional[str] = None,
    limit: int = Query(default=10, ge=1, le=100),
    request: Request = None
):
    """Find nodes related to a given node."""
    services = request.app.state.services
    graph_service = services.get("graph")
    
    if not graph_service:
        raise HTTPException(status_code=503, detail="Graph service not available")
    
    related = await graph_service.find_related(node_id, relationship_type)
    
    return {
        "node_id": node_id,
        "related": related,
        "count": len(related)
    }


@router.get("/changes")
async def what_changed(
    repo: str,
    since: Optional[str] = None,
    until: Optional[str] = None
):
    """Get changes in repository over time."""
    # TODO: Implement with git history analysis
    return {
        "repo": repo,
        "changes": [],
        "message": "Not implemented yet"
    }
