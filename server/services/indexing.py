"""Indexing Service - repository parsing and sync."""

from pathlib import Path
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

if TYPE_CHECKING:
    from kronos.types import NodeType

logger = logging.getLogger(__name__)


@dataclass
class IndexJob:
    """A queued indexing job."""
    id: str
    repo_path: str
    force: bool = False
    status: str = "pending"  # pending, running, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class SyncStatus:
    """Repository sync status."""
    repo: str
    last_sync: Optional[datetime] = None
    status: str = "unknown"
    nodes_count: int = 0
    edges_count: int = 0


class IndexingService:
    """
    Service for parsing repositories and maintaining sync.
    
    Coordinates parsers, embeddings, and graph updates.
    """
    
    def __init__(self, graph_service=None, storage=None):
        """Initialize with graph service and storage."""
        self.graph_service = graph_service
        self.storage = storage
        self.job_queue: list[IndexJob] = []
        self.sync_status: dict[str, SyncStatus] = {}
        self._worker_task = None
    
    async def start_worker(self):
        """Start the background indexing worker."""
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._process_queue())
    
    async def stop_worker(self):
        """Stop the background worker."""
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None
    
    async def queue_index(self, path: str, force: bool = False) -> str:
        """Queue a repository for indexing."""
        import uuid
        job = IndexJob(
            id=str(uuid.uuid4()),
            repo_path=path,
            force=force
        )
        self.job_queue.append(job)
        return job.id
    
    async def get_job_status(self, job_id: str) -> Optional[IndexJob]:
        """Get status of an indexing job."""
        for job in self.job_queue:
            if job.id == job_id:
                return job
        return None
    
    async def get_sync_status(self, repo: str) -> SyncStatus:
        """Get sync status for a repository."""
        return self.sync_status.get(repo, SyncStatus(repo=repo))
    
    async def force_sync(self, repo_path: str) -> str:
        """Force sync: git pull + reindex."""
        # TODO: Implement git pull
        return await self.queue_index(repo_path, force=True)
    
    async def _process_queue(self):
        """Background worker to process indexing jobs."""
        while True:
            # Find next pending job
            pending = [j for j in self.job_queue if j.status == "pending"]
            
            if pending:
                job = pending[0]
                job.status = "running"
                job.started_at = datetime.now()
                
                try:
                    await self._index_repository(job)
                    job.status = "completed"
                except Exception as e:
                    job.status = "failed"
                    job.error = str(e)
                finally:
                    job.completed_at = datetime.now()
            
            await asyncio.sleep(1)  # Check queue every second
    
    async def _index_repository(self, job: IndexJob):
        """
        Index a repository.
        
        1. Walk file tree
        2. Parse each file with appropriate parser
        3. Generate embeddings
        4. Store nodes and edges in graph
        """
        from kronos.types import NodeType, RelationType
        from parsers import PythonParser, MarkdownParser, YamlParser
        import logging
        
        logger = logging.getLogger(__name__)
        
        path = Path(job.repo_path)
        if not path.exists():
            raise ValueError(f"Repository not found: {job.repo_path}")
        
        # Initialize parsers
        parsers = [
            PythonParser(),
            MarkdownParser(),
            YamlParser(),
        ]
        
        repo_name = path.name
        node_count = 0
        edge_count = 0
        
        logger.info(f"Indexing repository: {repo_name} at {path}")
        
        # Walk directory
        for file_path in path.rglob("*"):
            # Skip directories and hidden files
            if file_path.is_dir() or file_path.name.startswith("."):
                continue
            
            # Skip ignored paths
            rel_path = file_path.relative_to(path)
            if self._should_skip(str(rel_path)):
                continue
            
            # Find appropriate parser
            parser = None
            for p in parsers:
                if p.can_parse(str(file_path)):
                    parser = p
                    break
            
            if not parser:
                continue
            
            try:
                # Read file
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                
                # Parse
                result = parser.parse(content, str(rel_path))
                
                # Store file node
                file_node_id = await self.storage.store_node(
                    content=content[:1000],  # First 1KB as preview
                    node_type=NodeType.FILE,
                    path=str(rel_path),
                    metadata={
                        "name": file_path.name,
                        "language": parser.language,
                        "full_path": str(file_path),
                    },
                )
                node_count += 1
                
                # Store entities from file
                for entity in result.entities:
                    entity_type = self._map_entity_type(entity.type)
                    
                    entity_node_id = await self.storage.store_node(
                        content=entity.content,
                        node_type=entity_type,
                        path=f"{rel_path}#{entity.name}",
                        metadata={
                            "name": entity.name,
                            "language": parser.language,
                            "line_start": entity.line_start,
                            "line_end": entity.line_end,
                            "docstring": entity.docstring,
                            "signature": entity.signature,
                        },
                    )
                    node_count += 1
                    
                    # Create PART_OF edge to file
                    await self.storage.create_edge(
                        from_id=entity_node_id,
                        to_id=file_node_id,
                        relation=RelationType.PART_OF,
                    )
                    edge_count += 1
                    
                    # Handle imports
                    if entity.imports:
                        for imp in entity.imports[:10]:  # Limit edges
                            # TODO: Resolve import to actual node
                            pass
                
                if node_count % 10 == 0:
                    logger.info(f"Indexed {node_count} nodes, {edge_count} edges")
                    
            except Exception as e:
                logger.warning(f"Error parsing {file_path}: {e}")
                continue
        
        # Update sync status
        self.sync_status[repo_name] = SyncStatus(
            repo=repo_name,
            last_sync=datetime.now(),
            status="synced",
            nodes_count=node_count,
            edges_count=edge_count,
        )
        
        logger.info(f"Indexing complete: {node_count} nodes, {edge_count} edges")
    
    def _should_skip(self, path: str) -> bool:
        """Check if path should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".git",
            "node_modules",
            "venv",
            ".egg-info",
            "dist",
            "build",
        ]
        return any(pattern in path for pattern in skip_patterns)
    
    def _map_entity_type(self, entity_type: str) -> "NodeType":
        """Map parser entity type to NodeType."""
        from kronos.types import NodeType
        mapping = {
            "function": NodeType.FUNCTION,
            "method": NodeType.METHOD,
            "class": NodeType.CLASS,
            "section": NodeType.SECTION,
            "document": NodeType.DOCUMENT,
            "meta_yaml": NodeType.META_YAML,
        }
        return mapping.get(entity_type, NodeType.FILE)
    
    async def remove_repo(self, repo: str) -> bool:
        """Remove a repository from the index."""
        # TODO: Implement
        if repo in self.sync_status:
            del self.sync_status[repo]
            return True
        return False
    
    def get_queue_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "pending": len([j for j in self.job_queue if j.status == "pending"]),
            "running": len([j for j in self.job_queue if j.status == "running"]),
            "completed": len([j for j in self.job_queue if j.status == "completed"]),
            "failed": len([j for j in self.job_queue if j.status == "failed"]),
        }
