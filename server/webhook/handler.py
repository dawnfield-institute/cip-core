"""Webhook endpoint handler."""

import hmac
import hashlib
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Header

router = APIRouter()
logger = logging.getLogger("cip-server.webhook")


class WebhookHandler:
    """
    Handler for git webhooks.
    
    Supports GitHub, GitLab, and Bitbucket.
    """
    
    def __init__(
        self,
        indexing_service=None,
        github_secret: Optional[str] = None,
        gitlab_token: Optional[str] = None
    ):
        self.indexing_service = indexing_service
        self.github_secret = github_secret
        self.gitlab_token = gitlab_token
    
    def verify_github_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """Verify GitHub webhook signature."""
        if not self.github_secret:
            return True  # No secret configured, accept all
        
        expected = hmac.new(
            self.github_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    def verify_gitlab_token(self, token: str) -> bool:
        """Verify GitLab webhook token."""
        if not self.gitlab_token:
            return True
        return hmac.compare_digest(self.gitlab_token, token)
    
    async def handle_github_push(self, data: dict) -> dict:
        """Handle GitHub push event."""
        repo_name = data.get("repository", {}).get("name", "unknown")
        repo_full = data.get("repository", {}).get("full_name", "unknown")
        ref = data.get("ref", "")
        commits = data.get("commits", [])
        
        logger.info(f"GitHub push: {repo_name} {ref} ({len(commits)} commits)")
        
        # Skip non-main branches
        if not ref.endswith("/main") and not ref.endswith("/master"):
            return {
                "status": "ignored",
                "reason": "not main branch",
                "ref": ref
            }
        
        # Queue reindex
        if self.indexing_service:
            # TODO: Get repo path from name
            # await self.indexing_service.queue_index(repo_path)
            pass
        
        return {
            "status": "accepted",
            "event": "push",
            "repo": repo_name,
            "repository": repo_full,
            "commits": len(commits)
        }
    
    async def handle_gitlab_push(self, data: dict) -> dict:
        """Handle GitLab push event."""
        project_name = data.get("project", {}).get("name", "unknown")
        project_full = data.get("project", {}).get("path_with_namespace", "unknown")
        commits = data.get("commits", [])
        ref = data.get("ref", "")
        
        logger.info(f"GitLab push: {project_name} {ref} ({len(commits)} commits)")
        
        # Skip non-main branches
        if not ref.endswith("/main") and not ref.endswith("/master"):
            return {
                "status": "ignored",
                "reason": "not main branch",
                "ref": ref
            }
        
        return {
            "status": "accepted",
            "event": "push",
            "project": project_full,
            "commits": len(commits)
        }


# Global handler instance (set during app initialization)
_handler: Optional[WebhookHandler] = None


def set_handler(handler: WebhookHandler):
    """Set the global webhook handler."""
    global _handler
    _handler = handler


@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """
    Handle GitHub webhook events.
    
    Triggers on push events to reindex affected files.
    """
    if not _handler:
        raise HTTPException(status_code=503, detail="Webhook handler not initialized")
    
    payload = await request.body()
    
    # Verify signature
    if x_hub_signature_256:
        if not _handler.verify_github_signature(payload, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse event
    data = await request.json()
    
    if x_github_event == "push":
        return await _handler.handle_github_push(data)
    
    return {"status": "ignored", "event": x_github_event}


@router.post("/gitlab")
async def gitlab_webhook(
    request: Request,
    x_gitlab_token: Optional[str] = Header(None)
):
    """Handle GitLab webhook events."""
    if not _handler:
        raise HTTPException(status_code=503, detail="Webhook handler not initialized")
    
    # Verify token
    if x_gitlab_token:
        if not _handler.verify_gitlab_token(x_gitlab_token):
            raise HTTPException(status_code=401, detail="Invalid token")
    
    data = await request.json()
    event_type = data.get("object_kind", "unknown")
    
    if event_type == "push":
        return await _handler.handle_gitlab_push(data)
    
    return {"status": "ignored", "event": event_type}


@router.post("/bitbucket")
async def bitbucket_webhook(request: Request):
    """Handle Bitbucket webhook events."""
    if not _handler:
        raise HTTPException(status_code=503, detail="Webhook handler not initialized")
    
    data = await request.json()
    
    # Bitbucket uses different event structure
    push_data = data.get("push", {})
    if push_data:
        repo = data.get("repository", {}).get("name", "unknown")
        changes = push_data.get("changes", [])
        
        logger.info(f"Bitbucket push: {repo} ({len(changes)} changes)")
        
        return {
            "status": "accepted",
            "event": "push",
            "repo": repo,
            "changes": len(changes)
        }
    
    return {"status": "ignored"}
