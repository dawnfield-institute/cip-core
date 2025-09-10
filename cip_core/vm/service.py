"""
CIP VM Service Integration for AI-powered repository analysis.

This module enables triggering heavy computational tasks on a dedicated VM
with Ollama, GPU acceleration, and comprehensive AI analysis capabilities.
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path
import yaml

from ..utils import YamlParser


@dataclass
class VMServiceConfig:
    """Configuration for CIP VM service."""
    endpoint: str
    api_key: Optional[str] = None
    timeout: int = 300  # 5 minutes default
    ollama_models: List[str] = None
    
    def __post_init__(self):
        if self.ollama_models is None:
            self.ollama_models = ["llama3.1", "codellama", "mistral"]


@dataclass
class AnalysisJob:
    """Represents an analysis job on the VM."""
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    job_type: str  # "scrutiny", "metadata-update", "comprehension-score"
    repository_url: str
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class CIPVMService:
    """
    Interface to CIP VM service for AI-powered repository analysis.
    
    Handles triggering and monitoring of heavy computational tasks including:
    - Ollama-powered code analysis
    - Automated meta.yaml updates with AI insights
    - Comprehension scoring with multiple LLMs
    - Cross-repository scrutiny analysis
    """
    
    def __init__(self, config: VMServiceConfig):
        self.config = config
        self.session = requests.Session()
        
        if config.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {config.api_key}',
                'Content-Type': 'application/json'
            })
    
    def trigger_scrutiny_analysis(self, 
                                 repository_path: str,
                                 ollama_model: str = "llama3.1",
                                 analysis_depth: str = "comprehensive") -> AnalysisJob:
        """
        Trigger AI-powered scrutiny analysis on the VM.
        
        Args:
            repository_path: Path to repository or repo:// URL
            ollama_model: Ollama model to use for analysis
            analysis_depth: "quick", "standard", "comprehensive"
            
        Returns:
            AnalysisJob with job details
        """
        payload = {
            "job_type": "scrutiny",
            "repository_path": repository_path,
            "config": {
                "ollama_model": ollama_model,
                "analysis_depth": analysis_depth,
                "include_cross_repo": True,
                "generate_insights": True
            }
        }
        
        response = self.session.post(
            f"{self.config.endpoint}/api/v1/jobs",
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        job_data = response.json()
        return AnalysisJob(**job_data)
    
    def trigger_metadata_update(self,
                               repository_path: str,
                               ollama_model: str = "codellama",
                               auto_commit: bool = False) -> AnalysisJob:
        """
        Trigger AI-enhanced metadata update on the VM.
        
        Uses Ollama to analyze repository content and generate
        intelligent meta.yaml updates with semantic insights.
        """
        payload = {
            "job_type": "metadata-update",
            "repository_path": repository_path,
            "config": {
                "ollama_model": ollama_model,
                "auto_commit": auto_commit,
                "analyze_code_semantics": True,
                "generate_descriptions": True,
                "update_complexity_scores": True
            }
        }
        
        response = self.session.post(
            f"{self.config.endpoint}/api/v1/jobs",
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        job_data = response.json()
        return AnalysisJob(**job_data)
    
    def trigger_comprehension_benchmark(self,
                                      repository_path: str,
                                      models: List[str] = None,
                                      question_count: int = 50) -> AnalysisJob:
        """
        Trigger multi-model comprehension benchmarking on the VM.
        
        Tests multiple Ollama models against repository content
        to establish comprehension baselines.
        """
        if models is None:
            models = self.config.ollama_models
            
        payload = {
            "job_type": "comprehension-benchmark",
            "repository_path": repository_path,
            "config": {
                "models": models,
                "question_count": question_count,
                "generate_questions": True,
                "test_cross_repo": True,
                "save_baseline": True
            }
        }
        
        response = self.session.post(
            f"{self.config.endpoint}/api/v1/jobs",
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        
        job_data = response.json()
        return AnalysisJob(**job_data)
    
    def get_job_status(self, job_id: str) -> AnalysisJob:
        """Get current status of an analysis job."""
        response = self.session.get(
            f"{self.config.endpoint}/api/v1/jobs/{job_id}",
            timeout=30
        )
        response.raise_for_status()
        
        job_data = response.json()
        return AnalysisJob(**job_data)
    
    def wait_for_completion(self, job_id: str, 
                           poll_interval: int = 30,
                           max_wait: int = 1800) -> AnalysisJob:
        """
        Wait for job completion with polling.
        
        Args:
            job_id: Job identifier
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait
            
        Returns:
            Completed AnalysisJob
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            job = self.get_job_status(job_id)
            
            if job.status in ["completed", "failed"]:
                return job
                
            print(f"⏳ Job {job_id} status: {job.status}")
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {max_wait} seconds")
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models on the VM."""
        response = self.session.get(
            f"{self.config.endpoint}/api/v1/models",
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()["models"]
    
    def get_vm_status(self) -> Dict[str, Any]:
        """Get VM service health and resource status."""
        response = self.session.get(
            f"{self.config.endpoint}/api/v1/status",
            timeout=30
        )
        response.raise_for_status()
        
        return response.json()


class GitHubVMIntegration:
    """
    Integrates CIP VM service with GitHub Actions workflows.
    
    Generates workflow files that can trigger VM analysis
    and retrieve results for automated processing.
    """
    
    def generate_vm_workflow(self, 
                           workflow_name: str = "cip-vm-analysis",
                           triggers: List[str] = None) -> Dict[str, Any]:
        """Generate GitHub workflow that uses CIP VM service."""
        
        if triggers is None:
            triggers = ["workflow_dispatch", "schedule"]
        
        workflow = {
            "name": "CIP VM Analysis",
            "on": {}
        }
        
        # Add triggers
        if "workflow_dispatch" in triggers:
            workflow["on"]["workflow_dispatch"] = {
                "inputs": {
                    "analysis_type": {
                        "description": "Type of analysis to run",
                        "required": True,
                        "default": "scrutiny",
                        "type": "choice",
                        "options": ["scrutiny", "metadata-update", "comprehension-benchmark"]
                    },
                    "ollama_model": {
                        "description": "Ollama model to use",
                        "required": False,
                        "default": "llama3.1"
                    }
                }
            }
        
        if "schedule" in triggers:
            workflow["on"]["schedule"] = [
                {"cron": "0 2 * * 1"}  # Weekly on Monday at 2 AM
            ]
        
        # Job definition
        workflow["jobs"] = {
            "vm-analysis": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout",
                        "uses": "actions/checkout@v4"
                    },
                    {
                        "name": "Set up Python",
                        "uses": "actions/setup-python@v4",
                        "with": {"python-version": "3.11"}
                    },
                    {
                        "name": "Install CIP-Core",
                        "run": "pip install cip-core"
                    },
                    {
                        "name": "Trigger VM Analysis",
                        "env": {
                            "CIP_VM_ENDPOINT": "${{ secrets.CIP_VM_ENDPOINT }}",
                            "CIP_VM_API_KEY": "${{ secrets.CIP_VM_API_KEY }}"
                        },
                        "run": """
                          cip vm-trigger \\
                            --type="${{ github.event.inputs.analysis_type || 'scrutiny' }}" \\
                            --model="${{ github.event.inputs.ollama_model || 'llama3.1' }}" \\
                            --repository="${{ github.repository }}" \\
                            --wait \\
                            --output=vm-results.json
                        """
                    },
                    {
                        "name": "Process Results",
                        "run": """
                          if [ -f vm-results.json ]; then
                            echo "📊 Analysis Results:"
                            cat vm-results.json | jq '.'
                            
                            # Create issue if problems found
                            if jq -e '.results.issues | length > 0' vm-results.json > /dev/null; then
                              echo "⚠️ Issues found, creating GitHub issue"
                              # Add issue creation logic here
                            fi
                          fi
                        """
                    },
                    {
                        "name": "Upload Results",
                        "uses": "actions/upload-artifact@v3",
                        "with": {
                            "name": "cip-vm-analysis-results",
                            "path": "vm-results.json"
                        }
                    }
                ]
            }
        }
        
        return workflow
    
    def install_vm_workflow(self, repo_path: str, workflow_name: str = "cip-vm-analysis"):
        """Install VM analysis workflow in repository."""
        workflows_dir = Path(repo_path) / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow = self.generate_vm_workflow(workflow_name)
        workflow_path = workflows_dir / f"{workflow_name}.yml"
        
        with open(workflow_path, 'w') as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        print(f"✅ Generated VM workflow: {workflow_path}")


def load_vm_config(config_path: str = ".cip/vm-config.yaml") -> VMServiceConfig:
    """Load VM service configuration from file or environment."""
    import os
    
    # Try to load from file first
    if Path(config_path).exists():
        parser = YamlParser()
        config_data = parser.parse_file(config_path)
        return VMServiceConfig(**config_data)
    
    # Fall back to environment variables
    endpoint = os.getenv("CIP_VM_ENDPOINT")
    if not endpoint:
        raise ValueError("CIP VM endpoint not configured. Set CIP_VM_ENDPOINT environment variable.")
    
    return VMServiceConfig(
        endpoint=endpoint,
        api_key=os.getenv("CIP_VM_API_KEY"),
        timeout=int(os.getenv("CIP_VM_TIMEOUT", "300"))
    )
