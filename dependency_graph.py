import ast
import os
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import sys

# Hardcoded stdlib modules (simplified)
STANDARD_LIBS = set(sys.builtin_module_names) | {
    'os', 'sys', 'math', 're', 'json', 'time', 'typing', 'pathlib', 'itertools',
    'functools', 'subprocess', 'datetime', 'collections', 'threading', 'argparse',
    'logging', 'copy', 'enum', 'heapq', 'shutil', 'inspect', 'traceback', 'types'
}

def parse_imports(path):
    imports = {}
    for root, _, files in os.walk(path):
        for filename in files:
            if filename.endswith('.py'):
                module = os.path.splitext(filename)[0]
                with open(os.path.join(root, filename), 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read(), filename=filename)
                        names = {n.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import)}
                        froms = {n.module.split('.')[0] for n in ast.walk(tree)
                                 if isinstance(n, ast.ImportFrom) and n.module}
                        all_imports = names | froms
                        filtered = [imp for imp in all_imports if imp and imp not in STANDARD_LIBS]
                        imports[module] = filtered
                    except SyntaxError:
                        continue
    return imports

def build_graph(imports):
    G = nx.DiGraph()
    for mod, deps in imports.items():
        for dep in deps:
            G.add_edge(mod, dep)
    return G

def plot_graph(graph, filepath='deps_clean.png'):
    plt.figure(figsize=(14, 14))
    pos = nx.kamada_kawai_layout(graph)  # Clearer than circular
    nx.draw(graph, pos, with_labels=True, node_size=800, font_size=6,
            arrows=True, arrowstyle='-|>', node_color='lightblue', edge_color='gray')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    print(f"Clean dependency graph saved as {filepath}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src-path', required=True)
    args = parser.parse_args()

    imports = parse_imports(args.src_path)
    graph = build_graph(imports)
    plot_graph(graph)

if __name__ == '__main__':
    main()
