"""
Dependency Graph Generator for the SpiceCode CLI Project
Uses only pure Python libraries: networkx + matplotlib
"""

import os
import re
import argparse
import networkx as nx
import matplotlib.pyplot as plt

def find_python_files(src_path):
    py_files = []
    for root, _, files in os.walk(src_path):
        for f in files:
            if f.endswith('.py') and not f.startswith('__'):
                py_files.append(os.path.join(root, f))
    return py_files

IMPORT_RE = re.compile(r'^(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))')

def extract_dependencies(files, base_path):
    graph = nx.DiGraph()
    module_map = {}

    for f in files:
        rel = os.path.relpath(f, base_path)
        mod = rel[:-3].replace(os.path.sep, '.')
        module_map[f] = mod
        graph.add_node(mod)

    for f in files:
        src = open(f, 'r', encoding='utf-8').read().splitlines()
        src_mod = module_map[f]
        for line in src:
            m = IMPORT_RE.match(line.strip())
            if m:
                imported = m.group(1) or m.group(2)
                for path, mod in module_map.items():
                    if imported == mod or imported.startswith(mod + '.'):
                        graph.add_edge(src_mod, mod)
    return graph

def plot_graph(graph, filepath='deps.png'):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph, k=0.4, iterations=50)
    nx.draw(graph, pos, with_labels=True, node_size=2000, font_size=8, arrows=True, arrowstyle='-|>')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    print(f"Dependency graph image saved to {filepath}")

def main():
    parser = argparse.ArgumentParser(description='Generate dependency graph for a Python project (portable version)')
    parser.add_argument('--src-path', required=True, help='Path to source code root')
    args = parser.parse_args()

    files = find_python_files(args.src_path)
    if not files:
        print(f"No Python files found under {args.src_path}")
        return
    graph = extract_dependencies(files, args.src_path)
    plot_graph(graph)

if __name__ == '__main__':
    main()
