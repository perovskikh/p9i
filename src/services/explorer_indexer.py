"""
Explorer File Indexer - Scans and indexes project files.

Part of ADR-016b Explorer Agent Extended.
Extracts symbols (functions, classes) and builds import graphs.
"""

import ast
import hashlib
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class IndexedFile:
    """Represents an indexed file."""
    path: str
    relative_path: str
    size: int
    mtime: float
    language: str
    symbols: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


@dataclass
class CallGraphNode:
    """A node in the call graph."""
    file_path: str
    symbol_name: str
    symbol_type: str  # 'function', 'class', 'method'
    calls: List[str] = field(default_factory=list)  # Called symbols


@dataclass
class ProjectIndex:
    """Complete project index."""
    project_path: str
    files: List[IndexedFile]
    entry_points: List[Dict[str, Any]]
    total_files: int
    total_symbols: int
    indexed_at: str


class ExplorerFileIndexer:
    """
    Indexes project files for fast exploration.

    Features:
    - File scanning with language detection
    - Symbol extraction (functions, classes)
    - Import graph building
    - Entry point detection
    """

    # File size limits
    MAX_FILE_SIZE = 500_000  # 500KB - skip large files
    MAX_LINES = 5000  # Summarize larger files

    # Language detection
    EXTENSION_LANG = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
    }

    # Patterns for entry point detection
    ENTRY_PATTERNS = [
        r"^def\s+(main|run|start|serve|listen|main\s*\()",  # Python
        r"^function\s+(main|run|start|serve|listen)",  # JS/TS
        r"^func\s+(main|run|start|serve|listen)",  # Go
        r"^fn\s+(main|run|start)",  # Rust
        r"(?:async\s+)?def\s+handle_(?:request|command|event)",  # Handlers
        r"(?:app|router)\.(get|post|put|delete|patch)\(",  # Route handlers
    ]

    def __init__(self, project_path: str):
        """
        Initialize indexer for project.

        Args:
            project_path: Root path of project to index
        """
        self.project_path = Path(project_path).resolve()
        self._cache: Dict[str, IndexedFile] = {}

    async def scan(self, force_refresh: bool = False) -> ProjectIndex:
        """
        Scan project and build complete index.

        Args:
            force_refresh: Force full rescan even if files unchanged

        Returns:
            ProjectIndex with all indexed data
        """
        logger.info(f"Starting index scan for {self.project_path}")

        indexed_files = []
        all_symbols = []
        entry_points = []

        # Walk project tree
        for root, dirs, files in os.walk(self.project_path):
            # Skip hidden and common ignore dirs
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {
                'node_modules', '__pycache__', '.git', 'venv', 'env',
                'dist', 'build', '.pytest_cache', '.mypy_cache'
            }]

            for filename in files:
                file_path = os.path.join(root, filename)

                # Skip binary and large files
                if not self._should_index(file_path):
                    continue

                indexed_file = await self._index_file(file_path)
                if indexed_file:
                    indexed_files.append(indexed_file)
                    all_symbols.extend(indexed_file.symbols)

                    # Check for entry points
                    eps = self._find_entry_points_in_file(indexed_file)
                    entry_points.extend(eps)

        index = ProjectIndex(
            project_path=str(self.project_path),
            files=indexed_files,
            entry_points=entry_points,
            total_files=len(indexed_files),
            total_symbols=len(all_symbols),
            indexed_at=datetime.now().isoformat()
        )

        logger.info(f"Index scan complete: {len(indexed_files)} files, {len(all_symbols)} symbols")
        return index

    async def _index_file(self, file_path: str) -> Optional[IndexedFile]:
        """
        Index a single file.

        Args:
            file_path: Absolute path to file

        Returns:
            IndexedFile or None if skip
        """
        try:
            path = Path(file_path)
            stat = path.stat()

            # Check cache by mtime
            cache_key = str(path)
            if cache_key in self._cache:
                cached = self._cache[cache_key]
                if cached.mtime >= stat.st_mtime:
                    return cached

            # Read file
            if stat.st_size > self.MAX_FILE_SIZE:
                logger.debug(f"Skipping large file: {file_path}")
                return None

            content = path.read_text(encoding='utf-8', errors='ignore')
            rel_path = str(path.relative_to(self.project_path))
            language = self._detect_language(path)

            # Extract symbols and imports based on language
            if language == "python":
                symbols, imports, exports = self._extract_python_symbols(content)
            elif language in ("javascript", "typescript"):
                symbols, imports, exports = self._extract_js_symbols(content)
            else:
                symbols, imports, exports = self._extract_generic_symbols(content)

            indexed = IndexedFile(
                path=str(path),
                relative_path=rel_path,
                size=stat.st_size,
                mtime=stat.st_mtime,
                language=language,
                symbols=symbols,
                imports=imports,
                exports=exports
            )

            self._cache[cache_key] = indexed
            return indexed

        except Exception as e:
            logger.debug(f"Error indexing {file_path}: {e}")
            return None

    def _should_index(self, file_path: str) -> bool:
        """Check if file should be indexed."""
        path = Path(file_path)

        # Check extension
        if path.suffix not in self.EXTENSION_LANG:
            return False

        # Skip hidden files
        if path.name.startswith('.'):
            return False

        return True

    def _detect_language(self, path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        return self.EXTENSION_LANG.get(path.suffix)

    def _extract_python_symbols(self, content: str) -> tuple:
        """
        Extract symbols from Python file using AST.

        Returns:
            (symbols, imports, exports) tuple
        """
        symbols = []
        imports = []
        exports = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                # Classes
                if isinstance(node, ast.ClassDef):
                    symbols.append({
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })

                # Functions
                elif isinstance(node, ast.FunctionDef):
                    # Skip methods inside classes
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        symbols.append({
                            "name": node.name,
                            "type": "function",
                            "line": node.lineno,
                            "methods": []
                        })

                # Import statements
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    else:
                        if node.module:
                            imports.append(node.module)

                # Module-level exports (__all__)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "__all__":
                            if isinstance(node.value, (ast.List, ast.Tuple)):
                                exports = [e.value if isinstance(e, ast.Constant) else str(e)
                                          for e in node.value.elts]

        except SyntaxError:
            logger.debug("Parse error in Python file")
        except Exception as e:
            logger.debug(f"Error extracting Python symbols: {e}")

        return symbols, imports, exports

    def _extract_js_symbols(self, content: str) -> tuple:
        """Extract symbols from JavaScript/TypeScript using regex."""
        symbols = []
        imports = []
        exports = []

        # Function declarations: function name(...)
        func_pattern = r'(?:async\s+)?function\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, content):
            symbols.append({
                "name": match.group(1),
                "type": "function",
                "line": content[:match.start()].count('\n') + 1,
                "methods": []
            })

        # Class declarations: class Name...
        class_pattern = r'class\s+(\w+)'
        for match in re.finditer(class_pattern, content):
            symbols.append({
                "name": match.group(1),
                "type": "class",
                "line": content[:match.start()].count('\n') + 1,
                "methods": []
            })

        # Arrow functions assigned to const: const name = ...
        const_func_pattern = r'const\s+(\w+)\s*=\s*(?:async\s+)?\('
        for match in re.finditer(const_func_pattern, content):
            symbols.append({
                "name": match.group(1),
                "type": "function",
                "line": content[:match.start()].count('\n') + 1,
                "methods": []
            })

        # Import statements
        import_pattern = r'(?:import\s+.*?\s+from\s+)?[\'"]([^\'"]+)[\'"]'
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))

        # Export statements
        export_pattern = r'export\s+(?:default\s+)?(?:const|function|class|async\s+function)\s+(\w+)'
        for match in re.finditer(export_pattern, content):
            exports.append(match.group(1))

        return symbols, imports, exports

    def _extract_generic_symbols(self, content: str) -> tuple:
        """Generic symbol extraction using simple patterns."""
        symbols = []
        imports = []

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip if too long
            if len(line) > 200:
                continue

            # Simple patterns for various languages
            if match := re.match(r'\s*(?:func|fn|def|function|subroutine)\s+(\w+)', line):
                symbols.append({
                    "name": match.group(1),
                    "type": "function",
                    "line": i,
                    "methods": []
                })
            elif match := re.match(r'\s*(?:class|struct|interface|type)\s+(\w+)', line):
                symbols.append({
                    "name": match.group(1),
                    "type": "class",
                    "line": i,
                    "methods": []
                })

        return symbols, imports, []

    def _find_entry_points_in_file(self, indexed_file: IndexedFile) -> List[Dict[str, Any]]:
        """Find entry points in indexed file."""
        entry_points = []

        for symbol in indexed_file.symbols:
            name = symbol["name"].lower()
            line = symbol["line"]

            # Check against entry patterns
            for pattern in self.ENTRY_PATTERNS:
                if re.search(pattern, f"{symbol['type']} {name}", re.IGNORECASE):
                    entry_points.append({
                        "file": indexed_file.relative_path,
                        "line": line,
                        "symbol": symbol["name"],
                        "type": symbol["type"],
                        "critical": "main" in name
                    })
                    break

        return entry_points

    async def build_call_graph(self, start_file: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Build call graph starting from file.

        Args:
            start_file: Entry point file path
            max_depth: Maximum traversal depth

        Returns:
            Call graph as nested dict
        """
        graph = {
            "entry": start_file,
            "depth": 0,
            "calls": []
        }

        visited: Set[str] = set()
        await self._traverse_calls(start_file, graph, visited, 0, max_depth)

        return graph

    async def _traverse_calls(
        self,
        file_path: str,
        node: Dict[str, Any],
        visited: Set[str],
        depth: int,
        max_depth: int
    ) -> None:
        """Recursively traverse call graph."""
        if depth >= max_depth or file_path in visited:
            return

        visited.add(file_path)

        # Find file in index
        indexed = next((f for f in self._cache.values() if f.path == file_path), None)
        if not indexed:
            return

        # For each symbol in file, look for calls
        for symbol in indexed.symbols:
            symbol_name = symbol["name"]

            # Look for calls to other files/modules
            for imported in indexed.imports:
                if self._is_local_import(imported):
                    called_file = self._resolve_import(file_path, imported)
                    if called_file:
                        child = {
                            "symbol": symbol_name,
                            "file": called_file,
                            "depth": depth + 1,
                            "calls": []
                        }
                        node["calls"].append(child)
                        await self._traverse_calls(called_file, child, visited, depth + 1, max_depth)

    def _is_local_import(self, import_path: str) -> bool:
        """Check if import is local (not external package)."""
        return not any(external in import_path for external in [
            'numpy', 'pandas', 'django', 'flask', 'fastapi', 'react', 'vue',
            'node_modules', 'pypi', 'pip', 'npm', 'yarn'
        ])

    def _resolve_import(self, from_file: str, import_path: str) -> Optional[str]:
        """Resolve import to absolute file path."""
        from_dir = Path(from_file).parent

        # Try as relative import
        candidates = [
            from_dir / f"{import_path}.py",
            from_dir / import_path / "__init__.py",
            from_dir / ".." / f"{import_path}.py",
        ]

        for candidate in candidates:
            if candidate.exists():
                return str(candidate)

        return None

    def get_symbol_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find symbol by name across all indexed files."""
        for indexed in self._cache.values():
            for symbol in indexed.symbols:
                if symbol["name"] == name:
                    return {
                        "file": indexed.relative_path,
                        "line": symbol["line"],
                        "type": symbol["type"],
                        "symbol": symbol
                    }
        return None

    def get_import_graph(self) -> Dict[str, List[str]]:
        """Get import graph as adjacency list."""
        graph = {}
        for indexed in self._cache.values():
            graph[indexed.relative_path] = indexed.imports
        return graph

    def summarize_file(self, file_path: str, max_lines: int = 100) -> str:
        """
        Get file summary for large files.

        Args:
            file_path: File to summarize
            max_lines: Maximum lines to return

        Returns:
            First max_lines lines as summary
        """
        try:
            path = Path(file_path)
            content = path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            if len(lines) <= max_lines:
                return content

            # Return first max_lines with note
            summary = '\n'.join(lines[:max_lines])
            summary += f"\n\n... [{len(lines) - max_lines} more lines truncated]"
            return summary

        except Exception as e:
            return f"Error reading file: {e}"


# Helper function for quick hashing
def hash_query(query: str) -> str:
    """Create hash of search query for cache key."""
    return hashlib.md5(query.encode()).hexdigest()[:16]
