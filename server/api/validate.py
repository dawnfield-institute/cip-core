"""Validation API endpoints."""

from fastapi import APIRouter, UploadFile, File, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
import yaml
import logging

from services.validation import ValidationService

logger = logging.getLogger(__name__)
router = APIRouter()


class ValidationRequest(BaseModel):
    """Validation request for a repository path."""
    path: str
    checks: list[str] = ["compliance"]


class IssueResponse(BaseModel):
    """Validation issue response."""
    level: str
    code: str
    message: str
    path: Optional[str] = None
    line: Optional[int] = None


class ValidationResponse(BaseModel):
    """Validation result response."""
    valid: bool
    errors: list[IssueResponse] = []
    warnings: list[IssueResponse] = []
    score: float = 0.0


def _to_issue_response(issue) -> IssueResponse:
    """Convert ValidationIssue to IssueResponse."""
    return IssueResponse(
        level=issue.level,
        code=issue.code,
        message=issue.message,
        path=issue.path,
        line=issue.line
    )


@router.post("/repo", response_model=ValidationResponse)
async def validate_repo(request: ValidationRequest, req: Request):
    """
    Validate an entire repository for CIP compliance.
    
    Returns compliance score (0.0-1.0) and list of issues.
    """
    validation_service: ValidationService = req.app.state.services['validation']
    if not validation_service:
        raise HTTPException(status_code=503, detail="ValidationService unavailable")
    
    try:
        result = await validation_service.validate_repo(
            path=request.path,
            checks=request.checks
        )
        
        return ValidationResponse(
            valid=result.valid,
            errors=[_to_issue_response(e) for e in result.errors],
            warnings=[_to_issue_response(w) for w in result.warnings],
            score=result.score
        )
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/meta", response_model=ValidationResponse)
async def validate_meta(content: dict, req: Request):
    """
    Validate meta.yaml content against CIP schema.
    
    Checks required fields, types, and schema compliance.
    """
    validation_service: ValidationService = req.app.state.services['validation']
    if not validation_service:
        raise HTTPException(status_code=503, detail="ValidationService unavailable")
    
    try:
        result = await validation_service.validate_meta(content)
        
        return ValidationResponse(
            valid=result.valid,
            errors=[_to_issue_response(e) for e in result.errors],
            warnings=[_to_issue_response(w) for w in result.warnings],
            score=result.score
        )
    except Exception as e:
        logger.error(f"Meta validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/structure", response_model=ValidationResponse)
async def validate_structure(request: ValidationRequest, req: Request):
    """
    Validate repository structure (README, LICENSE, folder organization).
    """
    validation_service: ValidationService = req.app.state.services['validation']
    if not validation_service:
        raise HTTPException(status_code=503, detail="ValidationService unavailable")
    
    try:
        result = await validation_service.validate_structure(request.path)
        
        return ValidationResponse(
            valid=result.valid,
            errors=[_to_issue_response(e) for e in result.errors],
            warnings=[_to_issue_response(w) for w in result.warnings],
            score=result.score
        )
    except Exception as e:
        logger.error(f"Structure validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file", response_model=ValidationResponse)
async def validate_file(req: Request, file: UploadFile = File(...)):
    """
    Validate an uploaded meta.yaml file.
    
    Parses YAML and validates against CIP schema.
    """
    validation_service: ValidationService = req.app.state.services['validation']
    if not validation_service:
        raise HTTPException(status_code=503, detail="ValidationService unavailable")
    
    try:
        # Parse uploaded YAML
        content_bytes = await file.read()
        content_str = content_bytes.decode('utf-8')
        content = yaml.safe_load(content_str)
        
        if not isinstance(content, dict):
            raise HTTPException(status_code=400, detail="Invalid YAML: must be a dictionary")
        
        # Validate using meta validator
        result = await validation_service.validate_meta(content)
        
        return ValidationResponse(
            valid=result.valid,
            errors=[_to_issue_response(e) for e in result.errors],
            warnings=[_to_issue_response(w) for w in result.warnings],
            score=result.score
        )
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {str(e)}")
    except Exception as e:
        logger.error(f"File validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
