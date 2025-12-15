"""
Python Parser

Extracts functions, classes, methods, and imports from Python files.
"""

from __future__ import annotations

import ast
import logging
from typing import List, Optional

from .base import ParserBase, ParseResult, ParsedEntity

logger = logging.getLogger(__name__)


class PythonParser(ParserBase):
    """
    Parser for Python source files.
    
    Uses Python's ast module for accurate parsing.
    """
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".py", ".pyi"]
    
    @property
    def language(self) -> str:
        return "python"
    
    def parse(self, content: str, path: str) -> ParseResult:
        """Parse Python file and extract entities."""
        entities = []
        imports = []
        errors = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            errors.append(f"Syntax error: {e}")
            return ParseResult(
                path=path,
                language=self.language,
                entities=[],
                imports=[],
                errors=errors,
            )
        
        lines = content.split("\n")
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # Extract top-level entities
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                entities.append(self._parse_function(node, lines))
            elif isinstance(node, ast.AsyncFunctionDef):
                entities.append(self._parse_function(node, lines, is_async=True))
            elif isinstance(node, ast.ClassDef):
                entities.append(self._parse_class(node, lines))
        
        return ParseResult(
            path=path,
            language=self.language,
            entities=entities,
            imports=imports,
            errors=errors if errors else None,
        )
    
    def _parse_function(
        self,
        node: ast.FunctionDef,
        lines: List[str],
        is_async: bool = False,
        parent: str = None,
    ) -> ParsedEntity:
        """Parse a function/method definition."""
        # Get content
        start = node.lineno - 1
        end = node.end_lineno
        content = "\n".join(lines[start:end])
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        returns = ""
        if node.returns:
            returns = f" -> {ast.unparse(node.returns)}"
        
        signature = f"def {node.name}({', '.join(args)}){returns}"
        if is_async:
            signature = "async " + signature
        
        # Extract function calls
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(child.func.attr)
        
        return ParsedEntity(
            type="method" if parent else "function",
            name=node.name,
            content=content,
            line_start=node.lineno,
            line_end=node.end_lineno,
            docstring=docstring,
            signature=signature,
            parent=parent,
            calls=calls if calls else None,
        )
    
    def _parse_class(
        self,
        node: ast.ClassDef,
        lines: List[str],
    ) -> ParsedEntity:
        """Parse a class definition."""
        # Get content
        start = node.lineno - 1
        end = node.end_lineno
        content = "\n".join(lines[start:end])
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Get bases
        bases = [ast.unparse(base) for base in node.bases]
        signature = f"class {node.name}"
        if bases:
            signature += f"({', '.join(bases)})"
        
        # Get methods
        children = []
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                children.append(child.name)
        
        return ParsedEntity(
            type="class",
            name=node.name,
            content=content,
            line_start=node.lineno,
            line_end=node.end_lineno,
            docstring=docstring,
            signature=signature,
            children=children if children else None,
            metadata={"bases": bases} if bases else None,
        )
