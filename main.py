import ast
import sys
import networkx as nx
import matplotlib.pyplot as plt
from fsm_extractor import FSMExtractor


def build_fsm_graph(transitions):
    graph = nx.DiGraph()
    for src, dst, label in transitions:
        if src is not None and dst is not None:
            graph.add_edge(src, dst, label=label or "")
    return graph


def visualize_fsm(G):
    pos = nx.circular_layout(G)
    plt.figure(figsize=(12, 8))
    plt.title("FSM with Conditions and Triggers")

    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color="lightblue",
        edge_color="gray",
        node_size=2500,
        font_size=12,
        arrows=True,
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="darkred")
    plt.show()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract FSM from Python code")
    parser.add_argument("filename", help="Target Python file")
    parser.add_argument("state_var", nargs="?", default="state", help="State variable name")
    args = parser.parse_args()

    with open(args.filename, "r") as f:
        tree = ast.parse(f.read())

    extractor = FSMExtractor(state_var=args.state_var)
    extractor.visit(tree)

    print("Detected Transitions:")
    for src, dst, label in extractor.transitions:
        print(f"{src} -> {dst} [{label}]")

    graph = build_fsm_graph(extractor.transitions)
    visualize_fsm(graph)


if __name__ == "__main__":
    main()
