"""
Main automation coordinator for CIP operations.
"""

import yaml
from typing import Optional
from pathlib import Path

from ..schemas import MetaYamlSchema
from ..validators import ComplianceValidator
from .metadata_generator import DirectoryMetadataGenerator
from .github_workflows import GitHubWorkflowGenerator


class CIPAutomation:
    """
    Main automation coordinator for CIP operations.
    """
    
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).resolve()
        self.metadata_generator = DirectoryMetadataGenerator(str(self.repo_root))
        self.workflow_generator = GitHubWorkflowGenerator(str(self.repo_root))
        self.validator = ComplianceValidator()
    
    def bootstrap_repository(self, repository_type: str = "theory"):
        """Bootstrap a repository with complete CIP automation."""
        print(f"🚀 Bootstrapping CIP automation for {self.repo_root}")
        
        # 1. Initialize repository metadata
        schema = MetaYamlSchema()
        cip_dir = self.repo_root / '.cip'
        cip_dir.mkdir(exist_ok=True)
        
        meta_path = cip_dir / 'meta.yaml'
        if not meta_path.exists():
            template = schema.generate_template(repository_type)
            with open(meta_path, 'w') as f:
                yaml.dump(template, f, sort_keys=False)
            print(f"✅ Created {meta_path}")
        
        # 2. Generate directory metadata
        self.metadata_generator.process_repository()
        
        # 3. Install GitHub workflows
        self.workflow_generator.install_workflows()
        
        # 4. Validate everything
        report = self.validator.validate_repository(str(self.repo_root))
        print(f"\n📊 Initial compliance: {report.score:.1%}")
        
        return report
