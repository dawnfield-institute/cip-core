"""
Multi-repository navigation and content resolution.

Implements the repo:// URL scheme and cross-repository
content discovery as designed in the CIP specification.
"""
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from urllib.parse import urlparse
from dataclasses import dataclass

from ..utils import YamlParser


@dataclass
class RepositoryReference:
    """Represents a reference to content in a repository."""
    scheme: str  # "repo"
    repository: str  # "dawn-field-theory"
    path: str  # "foundational/mathematics/"
    fragment: Optional[str] = None  # Optional anchor/section


@dataclass
class ResolvedContent:
    """Result of resolving a repo:// URL to actual content."""
    repository_path: str
    content_path: str
    exists: bool
    content_type: str  # "directory", "file", "missing"
    metadata: Optional[Dict[str, Any]] = None


class RepositoryResolver:
    """
    Resolves repo:// URLs to actual file system paths.
    
    Handles the core multi-repository navigation by:
    1. Parsing repo:// URLs
    2. Finding repositories in the ecosystem
    3. Resolving paths within repositories
    4. Providing metadata about resolved content
    """
    
    def __init__(self, ecosystem_root: str = None):
        """
        Initialize resolver with ecosystem root directory.
        
        Args:
            ecosystem_root: Root directory containing all repositories.
                          If None, uses current working directory parent.
        """
        if ecosystem_root:
            self.ecosystem_root = Path(ecosystem_root).resolve()
        else:
            # Default: look for repositories in parent directory
            cwd = Path.cwd()
            self.ecosystem_root = cwd.parent if cwd.name in ['cip-core', 'dawn-field-theory'] else cwd
        
        self.yaml_parser = YamlParser()
        self._repository_cache = {}
        self._scan_repositories()
    
    def _scan_repositories(self):
        """Scan ecosystem root for repositories with CIP metadata."""
        if not self.ecosystem_root.exists():
            return
        
        for entry in self.ecosystem_root.iterdir():
            if not entry.is_dir():
                continue
                
            # Look for CIP metadata
            cip_meta = entry / '.cip' / 'meta.yaml'
            if cip_meta.exists():
                try:
                    metadata = self.yaml_parser.parse_file(cip_meta)
                    self._repository_cache[entry.name] = {
                        'path': entry,
                        'metadata': metadata,
                        'repository_role': metadata.get('repository_role', 'unknown')
                    }
                except Exception as e:
                    print(f"Warning: Could not parse {cip_meta}: {e}")
    
    def parse_repo_url(self, repo_url: str) -> RepositoryReference:
        """
        Parse a repo:// URL into components.
        
        Examples:
        - repo://dawn-field-theory/foundational/
        - repo://cip-core/schemas/meta_yaml.py
        - repo://fracton-sdk/examples/#usage
        """
        if not repo_url.startswith('repo://'):
            raise ValueError(f"Invalid repo URL scheme: {repo_url}")
        
        # Parse URL components
        parsed = urlparse(repo_url)
        
        # Extract repository name (netloc in URL terms)
        repository = parsed.netloc
        if not repository:
            raise ValueError(f"Missing repository name in URL: {repo_url}")
        
        # Extract path (remove leading slash)
        path = parsed.path.lstrip('/')
        
        return RepositoryReference(
            scheme='repo',
            repository=repository,
            path=path,
            fragment=parsed.fragment or None
        )
    
    def resolve_content(self, repo_url: str) -> ResolvedContent:
        """
        Resolve a repo:// URL to actual file system content.
        
        Args:
            repo_url: Repository URL to resolve
            
        Returns:
            ResolvedContent with resolution results
        """
        try:
            ref = self.parse_repo_url(repo_url)
        except ValueError as e:
            return ResolvedContent(
                repository_path="",
                content_path="",
                exists=False,
                content_type="missing",
                metadata={"error": str(e)}
            )
        
        # Find repository
        if ref.repository not in self._repository_cache:
            return ResolvedContent(
                repository_path="",
                content_path="",
                exists=False,
                content_type="missing",
                metadata={"error": f"Repository not found: {ref.repository}"}
            )
        
        repo_info = self._repository_cache[ref.repository]
        repo_path = repo_info['path']
        
        # Resolve content path
        if ref.path:
            content_path = repo_path / ref.path
        else:
            content_path = repo_path
        
        # Check if content exists and determine type
        if content_path.exists():
            if content_path.is_dir():
                content_type = "directory"
                # Try to load directory metadata
                meta_path = content_path / 'meta.yaml'
                metadata = None
                if meta_path.exists():
                    try:
                        metadata = self.yaml_parser.parse_file(meta_path)
                    except Exception:
                        pass
            else:
                content_type = "file"
                metadata = {
                    "size": content_path.stat().st_size,
                    "modified": content_path.stat().st_mtime
                }
            
            return ResolvedContent(
                repository_path=str(repo_path),
                content_path=str(content_path),
                exists=True,
                content_type=content_type,
                metadata=metadata
            )
        else:
            return ResolvedContent(
                repository_path=str(repo_path),
                content_path=str(content_path),
                exists=False,
                content_type="missing",
                metadata={"error": f"Path not found: {ref.path}"}
            )
    
    def list_repositories(self) -> Dict[str, Dict[str, Any]]:
        """List all discovered repositories in the ecosystem."""
        return {
            name: {
                'path': str(info['path']),
                'repository_role': info['repository_role'],
                'title': info['metadata'].get('title', name),
                'description': info['metadata'].get('description', ''),
                'version': info['metadata'].get('version', 'unknown')
            }
            for name, info in self._repository_cache.items()
        }
    
    def validate_ecosystem_links(self, repository_name: str) -> List[Dict[str, Any]]:
        """
        Validate all ecosystem links for a repository.
        
        Returns list of validation results for each link.
        """
        if repository_name not in self._repository_cache:
            return [{"error": f"Repository not found: {repository_name}"}]
        
        repo_info = self._repository_cache[repository_name]
        metadata = repo_info['metadata']
        ecosystem_links = metadata.get('ecosystem_links', {})
        
        results = []
        for link_name, repo_url in ecosystem_links.items():
            resolution = self.resolve_content(repo_url)
            results.append({
                'link_name': link_name,
                'url': repo_url,
                'exists': resolution.exists,
                'content_type': resolution.content_type,
                'error': resolution.metadata.get('error') if not resolution.exists else None
            })
        
        return results


class DependencyGraph:
    """
    Builds and analyzes dependency relationships between repositories.
    """
    
    def __init__(self, resolver: RepositoryResolver):
        self.resolver = resolver
    
    def build_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Build dependency graph from ecosystem links.
        
        Returns:
            Dictionary mapping repository names to their dependencies
        """
        repositories = self.resolver.list_repositories()
        dependency_graph = {}
        
        for repo_name in repositories:
            dependencies = []
            
            # Get repository metadata
            repo_info = self.resolver._repository_cache[repo_name]
            ecosystem_links = repo_info['metadata'].get('ecosystem_links', {})
            
            # Extract dependencies from ecosystem links
            for link_name, repo_url in ecosystem_links.items():
                try:
                    ref = self.resolver.parse_repo_url(repo_url)
                    if ref.repository != repo_name:  # Avoid self-references
                        dependencies.append(ref.repository)
                except ValueError:
                    continue
            
            dependency_graph[repo_name] = list(set(dependencies))  # Remove duplicates
        
        return dependency_graph
    
    def find_dependency_cycles(self) -> List[List[str]]:
        """Find circular dependencies in the ecosystem."""
        graph = self.build_dependency_graph()
        cycles = []
        
        def dfs(node, path, visited):
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited or node not in graph:
                return
            
            visited.add(node)
            path.append(node)
            
            for dependency in graph[node]:
                dfs(dependency, path.copy(), visited)
        
        visited = set()
        for repo in graph:
            if repo not in visited:
                dfs(repo, [], visited)
        
        return cycles
    
    def get_repository_metrics(self) -> Dict[str, Dict[str, int]]:
        """Get dependency metrics for each repository."""
        graph = self.build_dependency_graph()
        
        metrics = {}
        for repo in graph:
            # Count outgoing dependencies
            dependencies_count = len(graph[repo])
            
            # Count incoming dependencies (how many repos depend on this one)
            dependents_count = sum(1 for deps in graph.values() if repo in deps)
            
            metrics[repo] = {
                'dependencies': dependencies_count,
                'dependents': dependents_count,
                'centrality': dependencies_count + dependents_count
            }
        
        return metrics


class ContentDiscovery:
    """
    Discovers and indexes content across the multi-repository ecosystem.
    """
    
    def __init__(self, resolver: RepositoryResolver):
        self.resolver = resolver
    
    def discover_content_by_type(self, content_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover content of a specific type across all repositories.
        
        Args:
            content_type: Type of content to discover (e.g., 'experiments', 'documentation')
        """
        repositories = self.resolver.list_repositories()
        content_map = {}
        
        for repo_name, repo_info in repositories.items():
            repo_path = Path(repo_info['path'])
            content_items = []
            
            # Search for directories matching content type
            for item in repo_path.rglob('*'):
                if item.is_dir() and item.name.lower() == content_type.lower():
                    # Check if directory has metadata
                    meta_path = item / 'meta.yaml'
                    metadata = None
                    if meta_path.exists():
                        try:
                            metadata = self.resolver.yaml_parser.parse_file(meta_path)
                        except Exception:
                            pass
                    
                    content_items.append({
                        'path': str(item.relative_to(repo_path)),
                        'full_path': str(item),
                        'metadata': metadata,
                        'repo_url': f"repo://{repo_name}/{item.relative_to(repo_path)}/"
                    })
            
            if content_items:
                content_map[repo_name] = content_items
        
        return content_map
    
    def find_similar_content(self, query: str) -> List[Dict[str, Any]]:
        """
        Find content similar to query across repositories.
        
        Simple text-based search for now - can be enhanced with semantic search.
        """
        repositories = self.resolver.list_repositories()
        results = []
        
        query_lower = query.lower()
        
        for repo_name, repo_info in repositories.items():
            repo_path = Path(repo_info['path'])
            
            # Search in file names and metadata
            for item in repo_path.rglob('*.md'):
                if query_lower in item.name.lower():
                    results.append({
                        'repository': repo_name,
                        'path': str(item.relative_to(repo_path)),
                        'match_type': 'filename',
                        'repo_url': f"repo://{repo_name}/{item.relative_to(repo_path)}"
                    })
                
                # Search in meta.yaml files
                meta_path = item.parent / 'meta.yaml'
                if meta_path.exists():
                    try:
                        metadata = self.resolver.yaml_parser.parse_file(meta_path)
                        description = metadata.get('description', '').lower()
                        tags = ' '.join(metadata.get('tags', [])).lower()
                        
                        if query_lower in description or query_lower in tags:
                            results.append({
                                'repository': repo_name,
                                'path': str(item.relative_to(repo_path)),
                                'match_type': 'metadata',
                                'repo_url': f"repo://{repo_name}/{item.relative_to(repo_path)}"
                            })
                    except Exception:
                        continue
        
        return results[:50]  # Limit results
