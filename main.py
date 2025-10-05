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
    if len(sys.argv) < 2:
        print(
            "Usage: python fsm_extractor.py <target_python_file.py> [state_variable_name (default: state)]"
        )
        return

    filename = sys.argv[1]
    state_var = sys.argv[2] if 2 in sys.argv else "state"
    with open(filename, "r") as f:
        tree = ast.parse(f.read())

    extractor = FSMExtractor(state_var=state_var)
    extractor.visit(tree)

    print("Detected Transitions:")
    for src, dst, label in extractor.transitions:
        print(f"{src} -> {dst} [{label}]")

    graph = build_fsm_graph(extractor.transitions)
    visualize_fsm(graph)


if __name__ == "__main__":
    main()
