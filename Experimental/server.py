from flask import Flask, jsonify, request
import os
import osmnx as ox
import time

# Create a Flask application instance
app = Flask(__name__)

def get_speed(lat, lon):
    # Find the nearest node in the graph to the coordinates
    nearest_node = ox.distance.nearest_nodes(G, X=lon, Y=lat)
    print(f"Nearest node found: {nearest_node}")
    
    # Extract edges connected to the nearest node
    edges = list(G.edges(nearest_node, data=True))
    print(f"Edges connected to the nearest node: {edges}")
    
    # Filter edges to get those with speed limits
    edges_with_speed = [(u, v, d) for u, v, d in edges if 'maxspeed' in d]
    print(f"Edges with speed limits: {edges_with_speed}")
    
    # Print the nearest node and the associated speed limits
    if edges_with_speed:
        best_edge = edges_with_speed[0]
        road_name = best_edge[2].get('name', 'Unknown road')
        best_speed = best_edge[2]['maxspeed'].split(' ')[0]
        print(f"Speed limit of the '{road_name}': {best_speed}")
        return best_speed
    else:
        print("No speed limit information available for nearby roads.")
        return 0

# Define a POST endpoint
@app.route('/speed', methods=['POST'])
def submit_data():
    print("Received request on /speed endpoint")
    
    # Get JSON data from the request
    data = request.get_json()

    # Basic validation to check if data is present
    if not data:
        print("Error: No data provided")
        return jsonify({"error": "No data provided"}), 400

    # Extract specific fields from the data
    lat = data.get('lat')
    lon = data.get('lon')
    print(f"Extracted data - lat: {lat}, lon: {lon}")

    # Validate required fields
    if lat is None or lon is None:
        print("Error: Missing 'lat' or 'lon'")
        return jsonify({"error": "Missing 'lat' or 'lon'"}), 400
    
    # Call get_speed with the local file path
    speed_limit = get_speed(lat, lon)

    if isinstance(speed_limit, list):
        speed_limit = speed_limit[0]
    if speed_limit:
        speed_limit = speed_limit.split(' ')[0]
    
    response = {
        "message": "Speed limit retrieved successfully",
        "data": {
            "speed_limit": speed_limit
        }
    }
    print(f"Response: {response}")

    return jsonify(response), 200

def shutdown_server():
    print('server.py has ended.')
    os._exit(0)

# Define a shutdown endpoint
@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Shutdown request received.")
    response = jsonify({"message": "Server shutting down..."}), 200
    
    # Give the response and then shutdown
    shutdown_server()
    return response

# Run the Flask application
if __name__ == '__main__':
    print("Starting Flask application")
    file_path = "Experimental/Maps/map.graphml"

    print(f"Loading street network from file: {file_path}")

    # Measure the time taken to load the street network
    start_time = time.time()
    G = ox.load_graphml(file_path)
    end_time = time.time()

    load_time = end_time - start_time
    print(f"Street network loaded in {load_time:.2f} seconds")

    # Start flask server
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))