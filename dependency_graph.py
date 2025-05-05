import os
import ast
import argparse
import matplotlib.pyplot as plt
import networkx as nx

def extract_top_level_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=filepath)
        except SyntaxError:
            return set()
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def scan_directory_for_imports(src_path):
    dependency_map = {}
    for root, _, files in os.walk(src_path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                module_name = os.path.relpath(full_path, src_path).replace(os.sep, ".")[:-3]  # strip .py
                imports = extract_top_level_imports(full_path)
                dependency_map[module_name] = imports
    return dependency_map

def plot_dependency_graph(dependency_map):
    G = nx.DiGraph()

    for module, imports in dependency_map.items():
        for imp in imports:
            G.add_edge(module, imp)

    pos = nx.circular_layout(G)
    plt.figure(figsize=(12, 12))
    nx.draw(G, pos, with_labels=True, node_size=1000, font_size=8, arrows=True, edge_color='gray', node_color='lightblue')
    plt.title("Minimal Python Import Graph")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Draw a minimal import dependency graph.")
    parser.add_argument('--src-path', type=str, required=True, help='Path to your Python source code directory')
    args = parser.parse_args()

    dep_map = scan_directory_for_imports(args.src_path)
    plot_dependency_graph(dep_map)

if __name__ == "__main__":
    main()
