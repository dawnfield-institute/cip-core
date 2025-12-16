"""Generation API endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateMetaRequest(BaseModel):
    """Request to generate meta.yaml."""
    path: str
    style: str = "minimal"  # minimal, standard, comprehensive


class GenerateReadmeRequest(BaseModel):
    """Request to generate README."""
    path: str
    include_badges: bool = True
    include_toc: bool = True


class SummarizeRequest(BaseModel):
    """Request to summarize content."""
    content: str
    max_length: int = 200


class GenerationResponse(BaseModel):
    """Response from generation endpoints."""
    content: str
    format: str
    confidence: float
    suggestions: list[str] = []
    model_used: str = ""
    tokens: dict = {}


@router.post("/meta", response_model=GenerationResponse)
async def generate_meta(request: GenerateMetaRequest, req: Request):
    """Generate meta.yaml for a directory."""
    try:
        service = req.app.state.services.get('generation')
        if not service:
            raise HTTPException(status_code=503, detail="Generation service unavailable")
        
        logger.info(f"Generating meta.yaml for: {request.path} (style={request.style})")
        
        result = await service.generate_meta(
            path=request.path,
            style=request.style
        )
        
        if result.confidence == 0.0 and result.suggestions:
            raise HTTPException(status_code=400, detail=result.suggestions[0])
        
        return GenerationResponse(
            content=result.content,
            format=result.format,
            confidence=result.confidence,
            suggestions=result.suggestions,
            model_used=result.model_used,
            tokens={
                "prompt": result.prompt_tokens,
                "completion": result.completion_tokens,
                "total": result.prompt_tokens + result.completion_tokens
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating meta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/readme", response_model=GenerationResponse)
async def generate_readme(request: GenerateReadmeRequest, req: Request):
    """Generate README.md for a directory."""
    try:
        service = req.app.state.services.get('generation')
        if not service:
            raise HTTPException(status_code=503, detail="Generation service unavailable")
        
        logger.info(f"Generating README for: {request.path}")
        
        result = await service.generate_readme(
            path=request.path,
            include_badges=request.include_badges,
            include_toc=request.include_toc
        )
        
        if result.confidence == 0.0 and result.suggestions:
            raise HTTPException(status_code=400, detail=result.suggestions[0])
        
        return GenerationResponse(
            content=result.content,
            format=result.format,
            confidence=result.confidence,
            suggestions=result.suggestions,
            model_used=result.model_used,
            tokens={
                "prompt": result.prompt_tokens,
                "completion": result.completion_tokens,
                "total": result.prompt_tokens + result.completion_tokens
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating README: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary")
async def generate_summary(request: SummarizeRequest, req: Request):
    """Generate a summary of content."""
    try:
        service = req.app.state.services.get('generation')
        if not service:
            raise HTTPException(status_code=503, detail="Generation service unavailable")
        
        summary = await service.generate_summary(
            content=request.content,
            max_length=request.max_length
        )
        
        return {
            "summary": summary,
            "max_length": request.max_length,
            "actual_length": len(summary)
        }
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance")
async def enhance_meta(content: dict, req: Request):
    """Enhance existing meta.yaml with AI suggestions."""
    try:
        service = req.app.state.services.get('generation')
        if not service:
            raise HTTPException(status_code=503, detail="Generation service unavailable")
        
        enhanced, suggestions = await service.enhance_meta(content)
        
        return {
            "enhanced": enhanced,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error enhancing meta: {e}")
        raise HTTPException(status_code=500, detail=str(e))
