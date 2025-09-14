"""
Unified instruction generation engine.

This module provides the InstructionEngine class that consolidates and replaces
direct usage of instruction generation classes with a unified interface.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from ..engine.repository import RepositoryManager
from ..engine.core import InstructionResult
from ..instructions import CIPInstructionsGenerator, generate_cip_instructions


class InstructionEngine:
    """
    Unified system for all CIP instruction generation operations.
    
    This class consolidates and replaces direct usage of:
    - CIPInstructionsGenerator
    - generate_cip_instructions function
    
    Usage:
        engine = InstructionEngine(repo_manager)
        result = engine.generate_instructions(template)
    """
    
    def __init__(self, repo: RepositoryManager):
        """
        Initialize instruction engine.
        
        Args:
            repo: Repository manager instance
        """
        self.repo = repo
        
        # Initialize underlying generator (lazy loading)
        self._instruction_generator = None
    
    @property
    def generator(self):
        """Get instruction generator (lazy loaded)."""
        if self._instruction_generator is None:
            self._instruction_generator = CIPInstructionsGenerator(str(self.repo.path))
        return self._instruction_generator
    
    def generate_instructions(self, template: Optional[str] = None) -> InstructionResult:
        """
        Generate AI instruction files for repository navigation.
        
        Args:
            template: Optional instruction template name
            
        Returns:
            InstructionResult with generated files and status
        """
        try:
            # Use the unified generate_cip_instructions function
            generated_files = generate_cip_instructions(str(self.repo.path))
            
            # Create instructions file path
            instructions_file = str(self.repo.cip_directory / "instructions_v2.0.yaml")
            
            # Generate content summary
            content_lines = []
            content_lines.append("# CIP Instructions Generated")
            content_lines.append(f"Repository: {self.repo.path.name}")
            content_lines.append(f"Generated files: {len(generated_files)}")
            content_lines.append("")
            
            for instruction_type, file_path in generated_files.items():
                content_lines.append(f"- {instruction_type}: {file_path}")
            
            content = "\n".join(content_lines)
            
            return InstructionResult(
                success=True,
                instructions_file=instructions_file,
                content=content,
                errors=[]
            )
            
        except Exception as e:
            return InstructionResult(
                success=False,
                instructions_file="",
                content="",
                errors=[str(e)]
            )
    
    def validate_instructions(self) -> Dict[str, Any]:
        """
        Validate generated instruction files.
        
        Returns:
            Dictionary with validation results
        """
        try:
            validation_result = self.generator.validate_instructions()
            return validation_result
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
    
    def get_instruction_summary(self) -> Dict[str, Any]:
        """
        Get a summary of available instruction files.
        
        Returns:
            Dictionary with instruction file information
        """
        cip_dir = self.repo.cip_directory
        instruction_files = {}
        
        # Check for common instruction files
        for filename in ["instructions_v2.0.yaml", "core.yaml", "resource_guide.yaml"]:
            file_path = cip_dir / filename
            instruction_files[filename] = {
                "exists": file_path.exists(),
                "path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            }
        
        return {
            "cip_directory": str(cip_dir),
            "instruction_files": instruction_files,
            "total_files": sum(1 for f in instruction_files.values() if f["exists"])
        }
    
    def regenerate_all_instructions(self, force: bool = False) -> InstructionResult:
        """
        Regenerate all instruction files.
        
        Args:
            force: Whether to overwrite existing files
            
        Returns:
            InstructionResult with generation status
        """
        try:
            # Check if instructions exist and force is not set
            if not force:
                existing_files = []
                for filename in ["instructions_v2.0.yaml", "core.yaml", "resource_guide.yaml"]:
                    file_path = self.repo.cip_directory / filename
                    if file_path.exists():
                        existing_files.append(filename)
                
                if existing_files:
                    return InstructionResult(
                        success=False,
                        instructions_file="",
                        content="",
                        errors=[f"Instruction files exist: {', '.join(existing_files)}. Use force=True to overwrite."]
                    )
            
            # Generate instructions
            return self.generate_instructions()
            
        except Exception as e:
            return InstructionResult(
                success=False,
                instructions_file="",
                content="",
                errors=[str(e)]
            )
