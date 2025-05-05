import ast
import os
import argparse
import matplotlib.pyplot as plt
import networkx as nx
import sys

STANDARD_LIBS = set(sys.builtin_module_names) | {
    'os', 'sys', 'math', 're', 'json', 'time', 'typing', 'pathlib', 'itertools',
    'functools', 'subprocess', 'datetime', 'collections', 'threading', 'argparse',
    'logging', 'copy', 'enum', 'heapq', 'shutil', 'inspect', 'traceback', 'types'
}

def is_std_or_local(module):
    return (
        not module or
        module.startswith('.') or
        module in STANDARD_LIBS
    )

def get_external_imports_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return set()
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if not is_std_or_local(mod):
                    imports.add(mod)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split('.')[0]
                if not is_std_or_local(mod):
                    imports.add(mod)
    return imports

def collect_imports(path):
    all_imports = set()
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                all_imports |= get_external_imports_from_file(full_path)
    return all_imports

def plot_dependency_graph(imports, output="deps_clean.png"):
    G = nx.DiGraph()
    G.add_node("your_project")
    for imp in sorted(imports):
        G.add_edge("your_project", imp)

    pos = nx.circular_layout(G)  # NO scipy needed
    plt.figure(figsize=(8, 8))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500,
            font_size=10, font_weight='bold', edge_color='gray', arrows=True)
    plt.title("External Dependencies")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    print(f"Saved dependency graph as {output}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src-path", required=True)
    args = parser.parse_args()

    imports = collect_imports(args.src_path)
    plot_dependency_graph(imports)

if __name__ == "__main__":
    main()
