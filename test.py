import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

# Define the area of interest
place_name = "Georgetown, Texas, USA"

# Download the street network
G = ox.graph_from_place(place_name, network_type='drive')

# Define the coordinates (latitude, longitude)
latitude = 30.633
longitude = -97.670

# Find the nearest node in the graph to the coordinates
nearest_node = ox.distance.nearest_nodes(G, X=longitude, Y=latitude)

# Extract edges connected to the nearest node
edges = list(G.edges(nearest_node, data=True))

# Filter edges to get those with speed limits
edges_with_speed = [(u, v, d) for u, v, d in edges if 'maxspeed' in d]

# Print the nearest node and the associated speed limits
print(f"Nearest node: {nearest_node}")
if edges_with_speed:
    for u, v, data in edges_with_speed:
        print(f"From node {u} to node {v} with speed limit: {data['maxspeed']}")
else:
    print("No speed limit information available for nearby roads.")

# Prepare positions for plotting
pos = ox.graph_to_gdfs(G, nodes=True, edges=False, node_geometry=True)['geometry'].apply(lambda geom: (geom.x, geom.y)).to_dict()

# Plot the graph
fig, ax = plt.subplots(figsize=(12, 8))
# Draw the entire graph with gray edges
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), edge_color='gray', alpha=0.5, ax=ax)
# Highlight the nearest node
nx.draw_networkx_nodes(G, pos, nodelist=[nearest_node], node_color='r', node_size=100, ax=ax)
# Highlight edges with speed limits
nx.draw_networkx_edges(G, pos, edgelist=[(u, v) for u, v, d in edges_with_speed], edge_color='b', width=2, ax=ax)

# Save the plot to a file
plt.title(f"Nearest Node {nearest_node} and Nearby Roads")
plt.savefig("nearest_road_with_speed_limit.png")
