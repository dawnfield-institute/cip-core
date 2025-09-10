"""
Basic directory metadata generator for creating meta.yaml files.
"""

import os
import yaml
import fnmatch
from typing import List, Dict, Any
from pathlib import Path

from ..utils import YamlParser


class DirectoryMetadataGenerator:
    """
    Generates directory-level meta.yaml files automatically.
    
    Migrated and enhanced from the original generate_meta_yamls.py script.
    """
    
    # Enhanced semantic scope mapping
    SEMANTIC_SCOPE_MAP = {
        'tools': ['tools', 'utility', 'automation'],
        'docs': ['documentation', 'guides'],
        'experiments': ['experiments', 'research'],
        'models': ['models', 'ai', 'ml'],
        'utils': ['utils', 'tools', 'helpers'],
        'results': ['results', 'analysis', 'data'],
        'core': ['core', 'foundation'],
        'agents': ['agents', 'modeling', 'ai'],
        'compression': ['compression', 'utilities', 'data'],
        'entropy': ['entropy', 'recursion', 'field theory'],
        'learning': ['learning', 'CIMM', 'ml'],
        'optimization': ['optimization', 'CIMM', 'performance'],
        'visualization': ['visualization', 'tools', 'graphics'],
        'reference_material': ['reference', 'experiment', 'research'],
        'citations': ['citations', 'bibliography', 'references'],
        'blueprints': ['blueprints', 'design', 'architecture'],
        'cognition_index_protocol': ['protocol', 'cip', 'standards'],
        'devkit': ['development', 'sdk', 'tools'],
        'foundational': ['theory', 'mathematics', 'foundation'],
        'internal': ['internal', 'private', 'development'],
        'mcp': ['mcp', 'protocol', 'integration'],
        'resources': ['resources', 'assets', 'data'],
        'roadmaps': ['roadmap', 'planning', 'strategy'],
        'sdk': ['sdk', 'development', 'api'],
        'spikes': ['spikes', 'prototypes', 'experimental'],
        'workflows': ['workflows', 'automation', 'ci-cd'],
    }
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.gitignore_patterns = self._load_gitignore_patterns()
        self.yaml_parser = YamlParser()
    
    def _load_gitignore_patterns(self) -> List[str]:
        """Load and parse .gitignore patterns."""
        gitignore_path = self.repo_root / '.gitignore'
        patterns = []
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        
        return patterns
    
    def _is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored based on gitignore patterns."""
        # Use the exact same logic as original script
        rel_path = str(path.relative_to(self.repo_root))
        
        for pattern in self.gitignore_patterns:
            if pattern.endswith('/'):
                dir_pattern = pattern[:-1]
                if fnmatch.fnmatch(rel_path, dir_pattern) or fnmatch.fnmatch(path.name, dir_pattern):
                    return True
                # Check if any parent directory matches
                parts = rel_path.split(os.sep)
                for part in parts:
                    if fnmatch.fnmatch(part, dir_pattern):
                        return True
            else:
                # Handle file patterns
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(path.name, pattern):
                    return True
                # Check if pattern matches any part of the path
                parts = rel_path.split(os.sep)
                for part in parts:
                    if fnmatch.fnmatch(part, pattern):
                        return True
        
        return False
    
    def _get_semantic_scope(self, dirname: str) -> List[str]:
        """Get semantic scope for directory based on name."""
        return self.SEMANTIC_SCOPE_MAP.get(dirname.lower(), [dirname])
    
    def _get_child_dirs_and_files(self, path: Path) -> tuple[List[str], List[str]]:
        """Get child directories and files, excluding ignored items."""
        files = []
        child_dirs = []
        
        if not path.exists():
            return files, child_dirs
            
        for entry in sorted(path.iterdir()):
            # Skip hidden files/directories except .gitignore (same logic as original)
            if entry.name.startswith('.') and entry.name != '.gitignore':
                continue
                
            if self._is_ignored(entry):
                continue
                
            if entry.is_dir():
                child_dirs.append(entry.name)
            elif entry.name != 'meta.yaml':
                files.append(entry.name)
        
        return files, child_dirs
    
    def generate_directory_metadata(self, path: Path) -> Dict[str, Any]:
        """Generate metadata for a specific directory."""
        dirname = path.name
        files, child_dirs = self._get_child_dirs_and_files(path)
        
        metadata = {
            'schema_version': '2.0',
            'directory_name': dirname,
            'description': f"Auto-generated metadata for {dirname} directory.",
            'semantic_scope': self._get_semantic_scope(dirname),
            'files': files,
            'child_directories': child_dirs,
        }
        
        # Add CIP-specific enhancements
        if dirname in ['cognition_index_protocol', 'cip-core']:
            metadata['repository_role'] = 'protocol'
            metadata['ecosystem_links'] = {
                'theory': 'repo://dawn-field-theory/foundational/',
                'sdk': 'repo://fracton-sdk/'
            }
        
        return metadata
    
    def process_directory(self, path: Path, force: bool = False):
        """Process directory and all subdirectories recursively."""
        if self._is_ignored(path):
            return
        
        meta_path = path / 'meta.yaml'
        
        # Generate meta.yaml if it doesn't exist or force is True
        if not meta_path.exists() or force:
            metadata = self.generate_directory_metadata(path)
            with open(meta_path, 'w', encoding='utf-8') as f:
                yaml.dump(metadata, f, sort_keys=False, allow_unicode=True)
            print(f"✅ Generated meta.yaml at {meta_path}")
        
        # Recurse into subdirectories (using same filtering logic)
        for entry in path.iterdir():
            # Skip hidden directories except .gitignore (same as original)
            if entry.name.startswith('.') and entry.name != '.gitignore':
                continue
                
            if entry.is_dir() and not self._is_ignored(entry):
                self.process_directory(entry, force)
    
    def process_repository(self, force: bool = False):
        """Process entire repository starting from root."""
        print(f"🚀 Processing repository: {self.repo_root}")
        print(f"📋 Loaded {len(self.gitignore_patterns)} gitignore patterns")
        self.process_directory(self.repo_root, force)
