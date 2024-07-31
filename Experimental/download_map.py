import osmnx as ox
import os

dir_path = 'Maps'

if not os.path.exists(dir_path):
    os.makedirs(dir_path)

def download_and_save_as_graphml(file_path="Maps/AUS_DAL_map.graphml"):
    # Define the bounding box coordinates for Georgetown, Texas (left, bottom, right, top)
    left, bottom, right, top = -98.1400289734493, 30.07194267071515, -96.25525714157412, 33.286098847129324
    
    # Create a graph from the bounding box
    G = ox.graph_from_bbox(north=top, south=bottom, east=right, west=left, network_type='drive')
    
    # Save the graph to a GraphML file
    ox.save_graphml(G, file_path)

download_and_save_as_graphml()