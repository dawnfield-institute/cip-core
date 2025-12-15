"""Navigation Service - repo:// URI resolution."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import re


@dataclass
class ResolvedPath:
    """Resolved path from URI."""
    uri: str
    repo: str
    relative_path: str
    absolute_path: Optional[str] = None
    exists: bool = False
    is_directory: bool = False


@dataclass
class DirectoryEntry:
    """Entry in a directory listing."""
    name: str
    type: str  # "file" or "directory"
    path: str
    has_meta: bool = False
    description: Optional[str] = None


class NavigationService:
    """
    Service for repo:// URI resolution and navigation.
    
    Provides virtual filesystem view across repositories.
    """
    
    # Pattern: repo://repo-name/path/to/file
    URI_PATTERN = re.compile(r'^repo://([^/]+)/(.*)$')
    
    def __init__(self, repo_paths: dict[str, str] = None):
        """
        Initialize with repository paths.
        
        repo_paths: {"repo-name": "/absolute/path/to/repo"}
        """
        self.repo_paths = repo_paths or {}
        
    def register_repo(self, name: str, path: str):
        """Register a repository path."""
        self.repo_paths[name] = path
    
    async def resolve_uri(self, uri: str) -> ResolvedPath:
        """
        Resolve a repo:// URI to actual path.
        
        Example: repo://cip-core/server/main.py
        """
        match = self.URI_PATTERN.match(uri)
        if not match:
            return ResolvedPath(
                uri=uri,
                repo="",
                relative_path="",
                exists=False
            )
        
        repo_name, relative_path = match.groups()
        
        if repo_name not in self.repo_paths:
            return ResolvedPath(
                uri=uri,
                repo=repo_name,
                relative_path=relative_path,
                exists=False
            )
        
        base_path = Path(self.repo_paths[repo_name])
        full_path = base_path / relative_path
        
        return ResolvedPath(
            uri=uri,
            repo=repo_name,
            relative_path=relative_path,
            absolute_path=str(full_path),
            exists=full_path.exists(),
            is_directory=full_path.is_dir() if full_path.exists() else False
        )
    
    async def list_directory(
        self,
        path: str,
        repo: Optional[str] = None
    ) -> list[DirectoryEntry]:
        """List contents of a directory with metadata."""
        # Determine actual path
        if repo:
            if repo not in self.repo_paths:
                return []
            dir_path = Path(self.repo_paths[repo]) / path
        else:
            dir_path = Path(path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        entries = []
        for item in dir_path.iterdir():
            # Check for meta.yaml
            has_meta = False
            if item.is_dir():
                has_meta = (item / "meta.yaml").exists()
            
            entries.append(DirectoryEntry(
                name=item.name,
                type="directory" if item.is_dir() else "file",
                path=str(item),
                has_meta=has_meta
            ))
        
        return sorted(entries, key=lambda e: (e.type == "file", e.name))
    
    async def get_context_payload(self, path: str) -> Optional[dict]:
        """Get meta.yaml context payload for a path."""
        meta_path = Path(path)
        if meta_path.is_dir():
            meta_path = meta_path / "meta.yaml"
        
        if not meta_path.exists():
            return None
        
        import yaml
        with open(meta_path) as f:
            return yaml.safe_load(f)
    
    async def list_repos(self) -> list[dict]:
        """List all registered repositories."""
        return [
            {"name": name, "path": path}
            for name, path in self.repo_paths.items()
        ]
