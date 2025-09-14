"""
Repository management and operations.

This module handles repository-level state and operations,
replacing scattered path management and file discovery logic.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import yaml
import fnmatch
from dataclasses import dataclass
from enum import Enum


class ProjectType(Enum):
    """Repository project types."""
    THEORY = "theory"
    SDK = "sdk"
    PROTOCOL = "protocol"
    PROJECT = "project"
    DEVKIT = "devkit"
    MODELS = "models"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class DirectoryTree:
    """Represents a directory structure."""
    path: Path
    files: List[str]
    directories: List[str]
    metadata_files: List[str]
    
    @property
    def has_metadata(self) -> bool:
        """Check if directory has metadata files."""
        return len(self.metadata_files) > 0


class RepositoryManager:
    """
    Manages repository-level state and operations.
    Replaces: scattered path management, file discovery logic
    """
    
    def __init__(self, repo_path: str):
        self.path = Path(repo_path).resolve()
        self._config_cache: Optional[Dict[str, Any]] = None
        self._structure_cache: Optional[DirectoryTree] = None
        self._gitignore_patterns: Optional[List[str]] = None
    
    @property
    def root_path(self) -> Path:
        """Get the repository root path."""
        return self.path
    
    @property
    def cip_directory(self) -> Path:
        """Get the .cip directory path."""
        return self.path / ".cip"
    
    @property
    def has_cip_setup(self) -> bool:
        """Check if repository has CIP setup."""
        return self.cip_directory.exists()
    
    def get_directory_structure(self, path: Optional[Path] = None) -> DirectoryTree:
        """
        Get directory structure for the given path or repo root.
        Returns cached result if available.
        """
        target_path = path or self.path
        
        # Use cache for root directory
        if path is None and self._structure_cache:
            return self._structure_cache
        
        files = []
        directories = []
        metadata_files = []
        
        if target_path.exists():
            for entry in sorted(target_path.iterdir()):
                # Skip hidden files/directories except specific ones
                if entry.name.startswith('.') and entry.name not in ['.gitignore', '.cip']:
                    continue
                
                if self.is_ignored(entry):
                    continue
                
                if entry.is_dir():
                    directories.append(entry.name)
                else:
                    files.append(entry.name)
                    if entry.name in ['meta.yaml', 'map.yaml']:
                        metadata_files.append(entry.name)
        
        structure = DirectoryTree(
            path=target_path,
            files=files,
            directories=directories,
            metadata_files=metadata_files
        )
        
        # Cache root directory structure
        if path is None:
            self._structure_cache = structure
        
        return structure
    
    def find_files_by_pattern(self, pattern: str, path: Optional[Path] = None) -> List[Path]:
        """Find files matching a glob pattern."""
        search_path = path or self.path
        matches = []
        
        for file_path in search_path.rglob(pattern):
            if not self.is_ignored(file_path):
                matches.append(file_path)
        
        return matches
    
    def load_existing_metadata(self) -> Dict[str, Any]:
        """Load existing metadata from various sources."""
        metadata = {}
        
        # Load root meta.yaml
        root_meta = self.path / "meta.yaml"
        if root_meta.exists():
            with open(root_meta, 'r', encoding='utf-8') as f:
                metadata['root'] = yaml.safe_load(f)
        
        # Load .cip/core.yaml
        cip_config = self.cip_directory / "core.yaml"
        if cip_config.exists():
            with open(cip_config, 'r', encoding='utf-8') as f:
                metadata['config'] = yaml.safe_load(f)
        
        # Load map.yaml
        map_file = self.path / "map.yaml"
        if map_file.exists():
            with open(map_file, 'r', encoding='utf-8') as f:
                metadata['map'] = yaml.safe_load(f)
        
        return metadata
    
    def detect_project_type(self) -> ProjectType:
        """Detect repository project type based on structure and content."""
        structure = self.get_directory_structure()
        
        # Check for theory repository indicators
        theory_indicators = ['experiments', 'theory', 'research', 'papers']
        if any(name in structure.directories for name in theory_indicators):
            return ProjectType.THEORY
        
        # Check for SDK repository indicators
        sdk_indicators = ['src', 'lib', 'setup.py', 'pyproject.toml', 'package.json']
        if any(name in structure.files for name in sdk_indicators) or \
           any(name in structure.directories for name in ['src', 'lib']):
            return ProjectType.SDK
        
        # Check for protocol repository indicators
        protocol_indicators = ['spec', 'protocol', 'standards']
        if any(name in structure.directories for name in protocol_indicators):
            return ProjectType.PROTOCOL
        
        # Check for devkit indicators
        devkit_indicators = ['tools', 'devkit', 'development']
        if any(name in structure.directories for name in devkit_indicators):
            return ProjectType.DEVKIT
        
        # Default to project
        return ProjectType.PROJECT
    
    def is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored based on gitignore patterns."""
        if self._gitignore_patterns is None:
            self._load_gitignore_patterns()
        
        # Get relative path from repo root
        try:
            rel_path = path.relative_to(self.path)
            path_str = str(rel_path).replace('\\', '/')
        except ValueError:
            # Path is not under repo root
            return True
        
        # Check against gitignore patterns
        for pattern in self._gitignore_patterns:
            if fnmatch.fnmatch(path_str, pattern) or \
               fnmatch.fnmatch(path.name, pattern):
                return True
            
            # Handle directory patterns
            if pattern.endswith('/') and path.is_dir():
                dir_pattern = pattern.rstrip('/')
                if fnmatch.fnmatch(path_str, dir_pattern) or \
                   fnmatch.fnmatch(path.name, dir_pattern):
                    return True
        
        return False
    
    def _load_gitignore_patterns(self) -> None:
        """Load and parse .gitignore patterns."""
        patterns = []
        
        # Default patterns
        default_patterns = [
            '.git',
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.Python',
            'env',
            'venv',
            '.venv',
            'node_modules',
            '.DS_Store',
            'Thumbs.db',
            '*.egg-info',
            'dist',
            'build',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
        ]
        patterns.extend(default_patterns)
        
        # Load from .gitignore file
        gitignore_path = self.path / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        self._gitignore_patterns = patterns
    
    def save_metadata(self, metadata: Dict[str, Any], path: str) -> None:
        """Save metadata to a YAML file."""
        file_path = self.path / path
        
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)
    
    def get_all_metadata_files(self) -> List[Path]:
        """Get all metadata files in the repository."""
        return self.find_files_by_pattern("meta.yaml")
    
    def get_child_directories_and_files(self, path: Optional[Path] = None) -> Tuple[List[str], List[str]]:
        """Get child directories and files for a given path."""
        structure = self.get_directory_structure(path)
        return structure.directories, structure.files
    
    def ensure_cip_structure(self) -> None:
        """Ensure basic CIP directory structure exists."""
        # Create .cip directory
        self.cip_directory.mkdir(exist_ok=True)
        
        # Create cognition directory
        cognition_dir = self.path / "cognition"
        cognition_dir.mkdir(exist_ok=True)
    
    def clear_cache(self) -> None:
        """Clear cached data (useful for testing or after changes)."""
        self._config_cache = None
        self._structure_cache = None
        self._gitignore_patterns = None
