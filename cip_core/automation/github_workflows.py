"""
GitHub workflow generator for CIP automation.
"""

import yaml
from typing import Dict, Any
from pathlib import Path


class GitHubWorkflowGenerator:
    """
    Generates GitHub Actions workflows for CIP automation.
    """
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.workflows_dir = self.repo_root / '.github' / 'workflows'
    
    def generate_cip_validation_workflow(self) -> Dict[str, Any]:
        """Generate GitHub workflow for CIP validation."""
        return {
            'name': 'CIP Validation',
            'on': {
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main']},
            },
            'jobs': {
                'validate-cip': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Checkout',
                            'uses': 'actions/checkout@v4'
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install CIP-Core',
                            'run': 'pip install cip-core'
                        },
                        {
                            'name': 'Validate CIP Compliance',
                            'run': 'cip validate --format=json > cip-report.json'
                        },
                        {
                            'name': 'Upload CIP Report',
                            'uses': 'actions/upload-artifact@v3',
                            'with': {
                                'name': 'cip-compliance-report',
                                'path': 'cip-report.json'
                            }
                        }
                    ]
                }
            }
        }
    
    def generate_metadata_update_workflow(self) -> Dict[str, Any]:
        """Generate workflow to automatically update meta.yaml files."""
        return {
            'name': 'Update CIP Metadata',
            'on': {
                'schedule': [{'cron': '0 2 * * 1'}],  # Weekly on Monday
                'workflow_dispatch': {}
            },
            'jobs': {
                'update-metadata': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'name': 'Checkout',
                            'uses': 'actions/checkout@v4',
                            'with': {'token': '${{ secrets.GITHUB_TOKEN }}'}
                        },
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install CIP-Core',
                            'run': 'pip install cip-core'
                        },
                        {
                            'name': 'Generate Directory Metadata',
                            'run': 'cip generate-metadata --force'
                        },
                        {
                            'name': 'Commit Changes',
                            'run': '''
                              git config --local user.email "action@github.com"
                              git config --local user.name "GitHub Action"
                              git add -A
                              git diff --staged --quiet || git commit -m "🤖 Auto-update CIP metadata"
                              git push
                            '''
                        }
                    ]
                }
            }
        }
    
    def install_workflows(self):
        """Install CIP workflows in repository."""
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # CIP Validation workflow
        validation_workflow = self.generate_cip_validation_workflow()
        validation_path = self.workflows_dir / 'cip-validation.yml'
        with open(validation_path, 'w') as f:
            yaml.dump(validation_workflow, f, sort_keys=False)
        print(f"✅ Generated {validation_path}")
        
        # Metadata update workflow
        metadata_workflow = self.generate_metadata_update_workflow()
        metadata_path = self.workflows_dir / 'cip-metadata-update.yml'
        with open(metadata_path, 'w') as f:
            yaml.dump(metadata_workflow, f, sort_keys=False)
        print(f"✅ Generated {metadata_path}")
