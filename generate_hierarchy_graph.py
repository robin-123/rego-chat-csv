import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

# --- Configuration ---
# Make sure this path is correct on your local machine
csv_file_path = r"C:\Users\DELL\Downloads\metamodel_Huawei (2).csv"

# --- Filtering Configuration (Set to None to visualize entire graph) ---
# Example: filter_parent_type = "ENODEBFUNCTION"
filter_parent_type = None # Set to a specific parent type name (e.g., "ENODEBFUNCTION") to filter

# --- Data Loading ---
if not os.path.exists(csv_file_path):
    print(f"Error: File not found at {csv_file_path}")
    print("Please update 'csv_file_path' in the script to the correct location of your metamodel_Huawei.csv file.")
    exit()

try:
    df = pd.read_csv(csv_file_path)
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit()

# --- Graph Creation ---
G = nx.DiGraph()

# Collect all nodes that should be included based on the filter
filtered_nodes = set()
if filter_parent_type:
    # Start with the filter_parent_type itself
    filtered_nodes.add(filter_parent_type)
    # Recursively add all children and their descendants
    queue = [filter_parent_type]
    while queue:
        current_node = queue.pop(0)
        children_df = df[df['metamodel_type_parent_types'].astype(str).str.contains(current_node, na=False)]
        for _, row in children_df.iterrows():
            child_name = row['metamodel_type_name']
            if child_name not in filtered_nodes:
                filtered_nodes.add(child_name)
                queue.append(child_name)

# Add nodes and edges based on filter
for index, row in df.iterrows():
    child_name = row["metamodel_type_name"]
    parent_types_str = str(row["metamodel_type_parent_types"])

    # Only process if child is in the filtered set (or no filter is applied)
    if not filter_parent_type or child_name in filtered_nodes:
        G.add_node(child_name)

        if parent_types_str and parent_types_str.lower() != "false" and parent_types_str.lower() != "nan":
            parent_types = [p.strip() for p in parent_types_str.split(',')]
            for parent_name in parent_types:
                # Only add edge if both parent and child are in the filtered set (or no filter)
                if not filter_parent_type or (parent_name in filtered_nodes and child_name in filtered_nodes):
                    G.add_node(parent_name) # Ensure parent node exists
                    G.add_edge(parent_name, child_name)

# --- Visualization ---
plt.figure(figsize=(15, 10)) # Adjust figure size as needed

# Use a layout algorithm (e.g., spring_layout, kamada_kawai_layout, planar_layout)
# For hierarchical data, a 'dot' layout (from Graphviz) is often best, but requires Graphviz installation.
# If Graphviz is not installed, spring_layout is a good general-purpose choice.
try:
    # Try using Graphviz layout if available (requires pygraphviz or pydot and Graphviz installed)
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
except ImportError:
    print("Graphviz layout not available. Falling back to spring_layout.")
    print("For better hierarchical layouts, consider installing Graphviz and pygraphviz/pydot.")
    pos = nx.spring_layout(G, k=0.5, iterations=50) # k regulates distance between nodes

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000, alpha=0.9)

# Draw edges
nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

plt.title("Hierarchical Diagram of Metamodel Types")
plt.axis('off') # Hide axes
plt.tight_layout() # Adjust layout to prevent labels overlapping
plt.show()

print("\nGraph visualization generated. A new window should have appeared with the diagram.")
print("If no window appeared, check your Python environment and Matplotlib backend.")