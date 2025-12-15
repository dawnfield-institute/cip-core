"""Tests for webhook handling."""

import pytest
import hmac
import hashlib
import json


class TestWebhookHandler:
    """Tests for WebhookHandler."""
    
    def test_verify_github_signature_valid(self):
        """Test verifying valid GitHub signature."""
        from webhook import WebhookHandler
        
        secret = "test-secret"
        payload = b'{"test": "data"}'
        
        # Create valid signature
        signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        handler = WebhookHandler(github_secret=secret)
        assert handler.verify_github_signature(payload, signature) is True
    
    def test_verify_github_signature_invalid(self):
        """Test verifying invalid GitHub signature."""
        from webhook import WebhookHandler
        
        secret = "test-secret"
        payload = b'{"test": "data"}'
        signature = "sha256=invalid"
        
        handler = WebhookHandler(github_secret=secret)
        assert handler.verify_github_signature(payload, signature) is False
    
    def test_verify_gitlab_token_valid(self):
        """Test verifying valid GitLab token."""
        from webhook import WebhookHandler
        
        token = "test-secret"
        
        handler = WebhookHandler(gitlab_token=token)
        assert handler.verify_gitlab_token(token) is True
    
    def test_verify_gitlab_token_invalid(self):
        """Test verifying invalid GitLab token."""
        from webhook import WebhookHandler
        
        secret = "test-secret"
        token = "wrong-secret"
        
        handler = WebhookHandler(gitlab_token=secret)
        assert handler.verify_gitlab_token(token) is False
    
    @pytest.mark.asyncio
    async def test_handle_github_push(self):
        """Test handling GitHub push event."""
        from webhook import WebhookHandler
        
        handler = WebhookHandler(github_secret="test")
        
        payload = {
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "user/repo",
                "clone_url": "https://github.com/user/repo.git"
            }
        }
        
        result = await handler.handle_github_push(payload)
        
        assert result is not None
        assert "repository" in result
    
    @pytest.mark.asyncio
    async def test_handle_gitlab_push(self):
        """Test handling GitLab push event."""
        from webhook import WebhookHandler
        
        handler = WebhookHandler(gitlab_token="test")
        
        payload = {
            "ref": "refs/heads/main",
            "project": {
                "path_with_namespace": "user/repo",
                "git_http_url": "https://gitlab.com/user/repo.git"
            }
        }
        
        result = await handler.handle_gitlab_push(payload)
        
        assert result is not None
        assert "project" in result
    
    @pytest.mark.asyncio
    async def test_handle_push_non_main_branch(self):
        """Test handling push to non-main branch (should ignore)."""
        from webhook import WebhookHandler
        
        handler = WebhookHandler(github_secret="test")
        
        payload = {
            "ref": "refs/heads/feature-branch",
            "repository": {
                "full_name": "user/repo"
            }
        }
        
        result = await handler.handle_github_push(payload)
        
        # Should skip non-main branches
        assert result is None or "ignored" in str(result).lower()


class TestWebhookEndpoints:
    """Tests for webhook API endpoints."""
    
    def test_github_webhook_endpoint(self):
        """Test GitHub webhook endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from webhook import router
        
        app = FastAPI()
        app.include_router(router, prefix="/webhook")
        
        client = TestClient(app)
        
        payload = {"test": "data"}
        payload_bytes = json.dumps(payload).encode()
        
        secret = "test-secret"
        signature = "sha256=" + hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        response = client.post(
            "/webhook/github",
            json=payload,
            headers={
                "X-Hub-Signature-256": signature,
                "X-GitHub-Event": "push"
            }
        )
        
        # Will fail without full setup, but endpoint should exist
        assert response.status_code in [200, 400, 401, 422, 503]
    
    def test_gitlab_webhook_endpoint(self):
        """Test GitLab webhook endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from webhook import router
        
        app = FastAPI()
        app.include_router(router, prefix="/webhook")
        
        client = TestClient(app)
        
        response = client.post(
            "/webhook/gitlab",
            json={"test": "data"},
            headers={
                "X-Gitlab-Token": "test-token",
                "X-Gitlab-Event": "Push Hook"
            }
        )
        
        # Will fail without full setup, but endpoint should exist
        assert response.status_code in [200, 400, 401, 422, 503]
    
    def test_bitbucket_webhook_endpoint(self):
        """Test Bitbucket webhook endpoint."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from webhook import router
        
        app = FastAPI()
        app.include_router(router, prefix="/webhook")
        
        client = TestClient(app)
        
        response = client.post(
            "/webhook/bitbucket",
            json={"test": "data"},
            headers={
                "X-Event-Key": "repo:push"
            }
        )
        
        # Will fail without full setup, but endpoint should exist
        assert response.status_code in [200, 400, 401, 422, 503]
