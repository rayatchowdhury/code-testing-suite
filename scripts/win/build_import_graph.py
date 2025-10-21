"""
Discovery Script 2: Import Graph Builder
Extracts import statements from all Python files in presentation layer.
Windows-compatible Python script.
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Repo root
REPO_ROOT = Path(__file__).parent.parent.parent
PRESENTATION_ROOT = REPO_ROOT / "src" / "app" / "presentation"
OUTPUT_DIR = REPO_ROOT / "refactor"
OUTPUT_FILE = OUTPUT_DIR / "import_graph.json"


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements."""
    
    def __init__(self):
        self.imports = []
        self.from_imports = []
    
    def visit_Import(self, node):
        """Handle 'import module' statements."""
        for alias in node.names:
            self.imports.append({
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Handle 'from module import name' statements."""
        module = node.module or ""
        level = node.level  # relative import level (0 = absolute)
        
        for alias in node.names:
            self.from_imports.append({
                "module": module,
                "name": alias.name,
                "alias": alias.asname,
                "level": level,
                "line": node.lineno
            })
        self.generic_visit(node)


def extract_imports_from_file(file_path: Path) -> Dict:
    """Extract imports from a Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
        
        visitor = ImportVisitor()
        visitor.visit(tree)
        
        return {
            "imports": visitor.imports,
            "from_imports": visitor.from_imports,
            "parse_error": None
        }
    except SyntaxError as e:
        return {
            "imports": [],
            "from_imports": [],
            "parse_error": f"SyntaxError at line {e.lineno}: {e.msg}"
        }
    except Exception as e:
        return {
            "imports": [],
            "from_imports": [],
            "parse_error": str(e)
        }


def build_import_graph(root: Path) -> Dict:
    """Build complete import graph for presentation layer."""
    graph = {
        "nodes": {},  # file -> {imports, from_imports}
        "edges": defaultdict(set),  # source_file -> {target_modules}
        "external_deps": defaultdict(int),  # external module -> count
        "internal_deps": defaultdict(int),  # internal module -> count
        "errors": []
    }
    
    python_files = list(root.rglob("*.py"))
    print(f"Analyzing {len(python_files)} Python files...")
    
    for file_path in python_files:
        rel_path = str(file_path.relative_to(root))
        
        # Extract imports
        result = extract_imports_from_file(file_path)
        
        # Store node data
        graph["nodes"][rel_path] = result
        
        # Track errors
        if result["parse_error"]:
            graph["errors"].append({
                "file": rel_path,
                "error": result["parse_error"]
            })
            continue
        
        # Build edges
        all_modules = set()
        
        # From direct imports
        for imp in result["imports"]:
            module = imp["module"]
            all_modules.add(module)
        
        # From from-imports
        for imp in result["from_imports"]:
            if imp["level"] == 0:  # absolute import
                module = imp["module"]
            else:  # relative import
                # Reconstruct module path
                current_package = rel_path.replace("\\", ".").replace("/", ".").rsplit(".", 1)[0]
                parent_parts = current_package.split(".")
                
                # Go up 'level' times
                if imp["level"] <= len(parent_parts):
                    parent = ".".join(parent_parts[:-imp["level"]] if imp["level"] else parent_parts)
                    module = f"{parent}.{imp['module']}" if imp["module"] else parent
                else:
                    module = imp["module"]
            
            if module:
                all_modules.add(module)
        
        # Classify as internal vs external
        for module in all_modules:
            graph["edges"][rel_path].add(module)
            
            if module.startswith("src.app.presentation") or module.startswith("app.presentation"):
                graph["internal_deps"][module] += 1
            else:
                graph["external_deps"][module] += 1
    
    # Convert sets to lists for JSON serialization
    graph["edges"] = {k: list(v) for k, v in graph["edges"].items()}
    
    return graph


def identify_circular_imports(graph: Dict) -> List[List[str]]:
    """Identify potential circular import chains (basic cycle detection)."""
    # This is a simplified version - just find direct circular references
    cycles = []
    edges = graph["edges"]
    
    for source, targets in edges.items():
        for target in targets:
            # Check if target imports source back
            target_file = target.replace(".", "\\") + ".py"
            if target_file in edges:
                if source.replace("\\", ".").replace(".py", "") in " ".join(edges[target_file]):
                    cycles.append([source, target_file])
    
    return cycles


def main():
    """Main import graph builder."""
    print("=" * 80)
    print("IMPORT GRAPH BUILDER")
    print("=" * 80)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Build import graph
    graph = build_import_graph(PRESENTATION_ROOT)
    
    # Statistics
    total_files = len(graph["nodes"])
    files_with_errors = len(graph["errors"])
    total_internal = sum(graph["internal_deps"].values())
    total_external = sum(graph["external_deps"].values())
    
    print(f"\nImport Graph Statistics:")
    print(f"  Total Python files: {total_files}")
    print(f"  Files with parse errors: {files_with_errors}")
    print(f"  Total internal imports: {total_internal}")
    print(f"  Total external imports: {total_external}")
    print(f"  Unique external modules: {len(graph['external_deps'])}")
    
    # Top external dependencies
    print("\nTop 10 external dependencies:")
    top_external = sorted(graph["external_deps"].items(), key=lambda x: x[1], reverse=True)[:10]
    for module, count in top_external:
        print(f"  {module}: {count} imports")
    
    # Circular imports
    cycles = identify_circular_imports(graph)
    if cycles:
        print(f"\n⚠ Potential circular imports detected: {len(cycles)}")
        for cycle in cycles[:5]:  # Show first 5
            print(f"  {' <-> '.join(cycle)}")
    
    # Save graph
    output = {
        "metadata": {
            "total_files": total_files,
            "files_with_errors": files_with_errors,
            "total_internal_imports": total_internal,
            "total_external_imports": total_external,
            "scan_date": "2025-10-21"
        },
        "graph": graph,
        "circular_imports": cycles
    }
    
    OUTPUT_FILE.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\n✓ Import graph complete. Output saved to: {OUTPUT_FILE}")
    print()


if __name__ == "__main__":
    main()
