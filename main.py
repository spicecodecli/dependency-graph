'''
Dependency Graph Generator for the SpiceCode CLI Project

This script parses all Python modules in the repository, extracts import relationships, and builds a dependency graph in Graphviz DOT format and as a plotted PNG.

Usage:
    python dependency_graph.py --src-path /path/to/spicecode

Requirements:
    pip install networkx graphviz matplotlib

Outputs:
    deps.dot   # Graphviz DOT
    deps.png   # Rendered dependency graph
'''
import os
import re
import argparse
import networkx as nx
from graphviz import Digraph
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
    # Map file paths to module names
    for f in files:
        rel = os.path.relpath(f, base_path)
        mod = rel[:-3].replace(os.path.sep, '.')
        module_map[f] = mod
        graph.add_node(mod)

    # Extract import edges
    for f in files:
        src = open(f, 'r', encoding='utf-8').read().splitlines()
        src_mod = module_map[f]
        for line in src:
            m = IMPORT_RE.match(line.strip())
            if m:
                imported = m.group(1) or m.group(2)
                # Only consider imports within project
                for path, mod in module_map.items():
                    if imported == mod or imported.startswith(mod + '.'):
                        graph.add_edge(src_mod, mod)
    return graph


def write_dot(graph, filepath='deps.dot'):
    dot = Digraph(comment='Dependency Graph')
    for n in graph.nodes():
        dot.node(n)
    for u, v in graph.edges():
        dot.edge(u, v)
    dot.render(filepath, format='dot', cleanup=True)
    print(f"Written DOT to {filepath}")


def plot_graph(graph, filepath='deps.png'):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph, k=0.5, iterations=50)
    nx.draw(graph, pos, with_labels=True, node_size=2000, font_size=8, arrowsize=12)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    print(f"Dependency graph image saved to {filepath}")


def main():
    parser = argparse.ArgumentParser(description='Generate dependency graph for a Python project')
    parser.add_argument('--src-path', required=True, help='Path to source code root')
    args = parser.parse_args()

    files = find_python_files(args.src_path)
    if not files:
        print(f"No Python files found under {args.src_path}")
        return
    graph = extract_dependencies(files, args.src_path)
    write_dot(graph)
    plot_graph(graph)

if __name__ == '__main__':
    main()
