import osmnx as ox
import os

dir_path = 'Maps'

if not os.path.exists(dir_path):
    os.makedirs(dir_path)

def download_and_save_as_graphml(file_path="Maps/georgetown_map.graphml"):
    # Define the bounding box coordinates for Georgetown, Texas (left, bottom, right, top)
    left, bottom, right, top = -97.84662785075604, 30.601071447149565, -97.60809443188543, 30.748176850389648

    # Create a graph from the bounding box
    G = ox.graph_from_bbox(north=top, south=bottom, east=right, west=left, network_type='drive')
    
    # Save the graph to a GraphML file
    ox.save_graphml(G, file_path)

download_and_save_as_graphml()