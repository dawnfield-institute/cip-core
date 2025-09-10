"""
CIP Instructions Generation System

Automatically generates AI-readable instructions and guidance files for 
repository navigation, understanding, and interaction following the
Cognition Index Protocol specifications.
"""
import re
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass

from ..utils import YamlParser
from ..navigation import RepositoryResolver


@dataclass
class InstructionTemplate:
    """Template for generating AI instructions."""
    schema_version: str
    instruction_type: str  # "usage", "navigation", "resource_guide", "core_orientation"
    description: str
    fields: Dict[str, Any]


class CIPInstructionsGenerator:
    """
    Generates AI instructions following CIP specifications.
    
    Creates comprehensive instruction files for AI agents to understand:
    - Repository structure and navigation
    - Meta.yaml schema interpretation 
    - Resource and document organization
    - Protocol-specific guidance
    """
    
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.yaml_parser = YamlParser()
        self.resolver = RepositoryResolver()
        
        # CIP directory
        self.cip_dir = self.repo_root / ".cip"
        self.cip_dir.mkdir(exist_ok=True)
    
    def analyze_repository_structure(self) -> Dict[str, Any]:
        """Analyze repository to understand structure for instruction generation."""
        
        structure = {
            "meta_yaml_files": [],
            "schema_versions": set(),
            "directory_hierarchy": {},
            "document_types": {},
            "experimental_files": [],
            "theory_documents": [],
            "blueprint_files": [],
        }
        
        # Find all meta.yaml files
        for meta_path in self.repo_root.rglob("meta.yaml"):
            try:
                meta_data = self.yaml_parser.parse_file(meta_path)
                rel_path = meta_path.relative_to(self.repo_root)
                
                structure["meta_yaml_files"].append({
                    "path": str(rel_path),
                    "directory": str(rel_path.parent),
                    "schema_version": meta_data.get("schema_version", "unknown"),
                    "semantic_scope": meta_data.get("semantic_scope", []),
                    "files": meta_data.get("files", [])
                })
                
                if "schema_version" in meta_data:
                    structure["schema_versions"].add(meta_data["schema_version"])
                    
            except Exception as e:
                print(f"⚠️  Could not parse {meta_path}: {e}")
        
        # Analyze document types by filename patterns
        for file_path in self.repo_root.rglob("*"):
            if file_path.is_file():
                filename = file_path.name
                
                # CIP filename tags
                if re.match(r'\[.*\]\[.*\].*\.md$', filename):
                    structure["experimental_files"].append(str(file_path.relative_to(self.repo_root)))
                
                # Blueprint files
                if 'blueprint' in str(file_path).lower():
                    structure["blueprint_files"].append(str(file_path.relative_to(self.repo_root)))
        
        return structure
    
    def generate_usage_instructions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate usage instructions for AI agents."""
        
        schema_versions = list(analysis["schema_versions"])
        latest_version = max(schema_versions) if schema_versions else "2.0"
        
        instructions = {
            "cip_version": latest_version,
            "meta_yaml_schema_version": latest_version,
            "description": """
This file provides instructions for using the Cognition Index Protocol (CIP) with meta.yaml schemas.
CIP agents should always look for a .cip directory in the repo root.
Use the instructions file to determine how to parse and interpret meta.yaml files.
When gathering context, consider not just the base-level directory but also all subdirectories.
When resolving paths, always use map.yaml as the canonical source of truth for repository structure.
            """.strip(),
            
            "MOST_IMPORTANT": [
                "Please ingest a document fully before giving opinions, metadata alone is insufficient.",
                "When asked about the Author, include INTENTIONS.md and CONTRIBUTION.md.",
                "Always check schema_version field in meta.yaml before parsing.",
                "Use .cip/core.yaml as directory-level orientation index.",
            ],
            
            "usage": {
                "schema_validation": f"Always check schema_version field before parsing meta.yaml (current: {latest_version})",
                "required_fields": ["schema_version", "directory_name", "description", "semantic_scope", "files", "child_directories"],
                "optional_fields": ["proficiency_level", "estimated_context_weight", "validation_type", "ai_analysis"],
                "navigation": "Use repository resolver for cross-repo navigation with repo:// URLs"
            },
            
            "repository_structure": {
                "total_directories": len(analysis["meta_yaml_files"]),
                "schema_versions_found": schema_versions,
                "experimental_files_count": len(analysis["experimental_files"]),
                "theory_documents_count": len(analysis["theory_documents"]),
                "blueprint_files_count": len(analysis["blueprint_files"])
            }
        }
        
        return instructions
    
    def generate_core_orientation(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate core.yaml orientation index."""
        
        core_index = {
            "schema_version": "2.0",
            "orientation_type": "directory_index",
            "description": "Directory-level orientation index for CIP navigation",
            "generated_date": "2025-09-10",
            
            "primary_directories": {},
            "document_categories": {
                "theory": [],
                "experiments": [],
                "blueprints": [],
                "tools": [],
                "documentation": []
            },
            
            "navigation_hints": {
                "foundational_theory": "foundational/",
                "experiments": "experiments/ and blueprints/",
                "tools_utilities": "tools/ and devkit/",
                "protocol_specs": "cognition_index_protocol/",
                "development": "sdk/ and models/"
            }
        }
        
        # Organize directories by semantic scope
        for meta_info in analysis["meta_yaml_files"]:
            directory = meta_info["directory"]
            semantic_scope = meta_info.get("semantic_scope", [])
            
            # Categorize by semantic scope
            if any(scope in ["theory", "foundational", "mathematics"] for scope in semantic_scope):
                core_index["document_categories"]["theory"].append(directory)
            elif any(scope in ["experiments", "testing", "validation"] for scope in semantic_scope):
                core_index["document_categories"]["experiments"].append(directory)
            elif any(scope in ["blueprints", "design", "architecture"] for scope in semantic_scope):
                core_index["document_categories"]["blueprints"].append(directory)
            elif any(scope in ["tools", "utilities", "automation"] for scope in semantic_scope):
                core_index["document_categories"]["tools"].append(directory)
            elif any(scope in ["documentation", "guides", "reference"] for scope in semantic_scope):
                core_index["document_categories"]["documentation"].append(directory)
            
            # Add to primary directories
            if directory and directory != ".":
                core_index["primary_directories"][directory] = {
                    "semantic_scope": semantic_scope,
                    "file_count": len(meta_info.get("files", [])),
                    "schema_version": meta_info.get("schema_version", "unknown")
                }
        
        return core_index
    
    def generate_resource_guide(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resource guide for document-level curation."""
        
        resource_guide = {
            "schema_version": "2.0",
            "guide_type": "document_curation",
            "description": "Document-level curation guide for CIP navigation and citation",
            "generated_date": "2025-09-10",
            
            "theories": [],
            "experiments": [],
            "blueprints": [],
            "tools": [],
            
            "usage_instructions": {
                "theory_citation": "Use theory documents to ground explanations and provide mathematical basis",
                "experiment_reference": "Reference experiments for validation and reproducibility examples", 
                "blueprint_integration": "Use blueprints for architectural guidance and design patterns",
                "tool_utilization": "Reference tools for automation and implementation guidance"
            }
        }
        
        # Organize theory documents
        theory_groups = {}
        for doc_path in analysis["theory_documents"]:
            # Extract theory category from path or filename
            if "entropy" in doc_path.lower() or "collapse" in doc_path.lower():
                category = "Entropy Collapse & Field Dynamics"
            elif "balance" in doc_path.lower() or "recursive" in doc_path.lower():
                category = "Recursive Balance Field & Quantum Potentials"
            elif "bifractal" in doc_path.lower() or "semantic" in doc_path.lower():
                category = "Bifractal Collapse & Semantic Recursion"
            else:
                category = "General Theory"
            
            if category not in theory_groups:
                theory_groups[category] = []
            theory_groups[category].append(doc_path)
        
        # Add to resource guide
        for category, documents in theory_groups.items():
            resource_guide["theories"].append({
                "name": category,
                "description": f"Theoretical framework for {category.lower()}",
                "documents": documents,
                "instruction": f"For topics involving {category.lower()}, reference these documents for theoretical foundation."
            })
        
        # Add experiments
        if analysis["experimental_files"]:
            resource_guide["experiments"] = [{
                "name": "CIP Protocol Experiments", 
                "description": "Protocol-driven experiments and validation studies",
                "documents": analysis["experimental_files"],
                "instruction": "Reference for reproducible experimental methodology and validation procedures."
            }]
        
        # Add blueprints
        if analysis["blueprint_files"]:
            resource_guide["blueprints"] = [{
                "name": "System Blueprints",
                "description": "Architectural designs and implementation blueprints", 
                "documents": analysis["blueprint_files"],
                "instruction": "Use for system architecture and design pattern guidance."
            }]
        
        return resource_guide
    
    def generate_all_instructions(self) -> Dict[str, str]:
        """Generate complete set of CIP instruction files."""
        
        print("🤖 Analyzing repository structure for instruction generation...")
        analysis = self.analyze_repository_structure()
        
        generated_files = {}
        
        # 1. Usage Instructions
        print("📋 Generating usage instructions...")
        usage_instructions = self.generate_usage_instructions(analysis)
        usage_path = self.cip_dir / "instructions_v2.0.yaml"
        with open(usage_path, 'w', encoding='utf-8') as f:
            yaml.dump(usage_instructions, f, sort_keys=False, allow_unicode=True)
        generated_files["usage_instructions"] = str(usage_path)
        
        # 2. Core Orientation Index
        print("🗺️  Generating core orientation index...")
        core_orientation = self.generate_core_orientation(analysis)
        core_path = self.cip_dir / "core.yaml"
        with open(core_path, 'w', encoding='utf-8') as f:
            yaml.dump(core_orientation, f, sort_keys=False, allow_unicode=True)
        generated_files["core_orientation"] = str(core_path)
        
        # 3. Resource Guide (if we have enough content)
        if analysis["theory_documents"] or analysis["experimental_files"]:
            print("📚 Generating resource guide...")
            resource_guide = self.generate_resource_guide(analysis)
            resource_path = self.cip_dir / "resource_guide.yaml"
            with open(resource_path, 'w', encoding='utf-8') as f:
                yaml.dump(resource_guide, f, sort_keys=False, allow_unicode=True)
            generated_files["resource_guide"] = str(resource_path)
        
        return generated_files
    
    def validate_instructions(self) -> Dict[str, Any]:
        """Validate generated instruction files."""
        validation_results = {
            "valid": True,
            "files_checked": [],
            "issues": []
        }
        
        # Check required files exist
        required_files = ["instructions_v2.0.yaml", "core.yaml"]
        for filename in required_files:
            file_path = self.cip_dir / filename
            validation_results["files_checked"].append(str(file_path))
            
            if not file_path.exists():
                validation_results["valid"] = False
                validation_results["issues"].append(f"Missing required file: {filename}")
            else:
                try:
                    self.yaml_parser.parse_file(file_path)
                except Exception as e:
                    validation_results["valid"] = False
                    validation_results["issues"].append(f"Invalid YAML in {filename}: {e}")
        
        return validation_results


def generate_cip_instructions(repo_path: str = ".") -> Dict[str, str]:
    """
    Generate complete CIP instruction set for a repository.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        Dictionary mapping instruction type to generated file path
    """
    generator = CIPInstructionsGenerator(repo_path)
    return generator.generate_all_instructions()
