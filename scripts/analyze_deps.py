import os
import re
from pathlib import Path

def analyze_dependencies(root_dir, search_dir, extensions, import_regex):
    graph = {}
    all_files = []
    for root, _, files in os.walk(search_dir):
        if "__pycache__" in root or "node_modules" in root:
            continue
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(root_dir).as_posix()
                all_files.append(rel_path)
                
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    imports = re.findall(import_regex, content)
                    graph[rel_path] = sorted(list(set(imports)))
    return graph, all_files

def main():
    root = Path("c:/Users/dace8/OneDrive/Documentos/Antigravity/oraculo-nueva-eternia")
    
    # Python analysis
    py_graph, py_files = analyze_dependencies(root, root / "src", [".py"], r'from\s+(src\.\S+)\s+import|import\s+(src\.\S+)')
    
    # TypeScript analysis
    ts_graph, ts_files = analyze_dependencies(root, root / "frontend/src", [".ts", ".tsx"], r'from\s+[\'"](\.\.?/\S+)[\'"]')

    # Output to file
    with open("dependency_audit.txt", "w") as f:
        f.write("PYTHON FILES:\n")
        f.write("\n".join(py_files) + "\n\n")
        f.write("PYTHON GRAPH:\n")
        for k, v in py_graph.items():
            f.write(f"{k} -> {v}\n")
            
        f.write("\nTS FILES:\n")
        f.write("\n".join(ts_files) + "\n\n")
        f.write("TS GRAPH:\n")
        for k, v in ts_graph.items():
            f.write(f"{k} -> {v}\n")

if __name__ == "__main__":
    main()
