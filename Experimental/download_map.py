import osmnx as ox
import os

dir_path = 'Maps'

if not os.path.exists(dir_path):
    os.makedirs(dir_path)

def download_and_save_as_graphml(file_path="Maps/map.graphml"):
    # Define the bounding box coordinates
    bottom, left = 30.610327077517546, -97.82914630749687
    top, right = 33.34599146415902, -96.27847196976995

    # Create a graph from the bounding box
    G = ox.graph_from_bbox(bbox=(top,bottom,right,left), network_type='drive')
    
    # Filter out edges that do not have a speed limit
    edges_with_speed = [(u, v, k) for u, v, k, data in G.edges(keys=True, data=True) if 'maxspeed' in data]

    # Create a new graph with only edges that have speed limits
    H = G.edge_subgraph(edges_with_speed).copy()

    # Save the filtered graph to a GraphML file
    ox.save_graphml(H, file_path)

download_and_save_as_graphml()