from flask import Flask, jsonify, request
import os
import random
import osmnx as ox

# Create a Flask application instance
app = Flask(__name__)

def get_speed(lat, lon):    
    # Download the street network
    G = ox.graph_from_point(center_point=(lat,lon), network_type='drive')
    
    # Find the nearest node in the graph to the coordinates
    nearest_node = ox.distance.nearest_nodes(G, X=lon, Y=lat)
    
    # Extract edges connected to the nearest node
    edges = list(G.edges(nearest_node, data=True))
    
    # Filter edges to get those with speed limits
    edges_with_speed = [(u, v, d) for u, v, d in edges if 'maxspeed' in d]
    
    # Print the nearest node and the associated speed limits
    print(f"Nearest node: {nearest_node}")
    if edges_with_speed:
        for u, v, data in edges_with_speed:
            print(f"From node {u} to node {v} with speed limit: {data['maxspeed']}")
            return data['maxspeed']
    else:
        print("No speed limit information available for nearby roads.")
        return 0

# Define a POST endpoint
@app.route('/speed', methods=['POST'])
def submit_data():
    # Get JSON data from the request
    data = request.get_json()

    # Basic validation to check if data is present
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract specific fields from the data
    lat = data.get('lat')
    lon = data.get('lon')

    print(f'Received: {lat}, {lon}')

    # Validate required fields
    if not lat or not lon:
        return jsonify({"error": "Missing 'lat' or 'lon'"}), 400
    
    speed_limit = get_speed(lat, lon)
    print(speed_limit)
    if speed_limit:
        speed_limit = speed_limit.split(' ')[0]

    response = {
        "message": "Speed limit retrieved successfully",
        "data": {
            "speed_limit": speed_limit #round(random.randint(5,85) / 5) * 5
        }
    }

    return jsonify(response), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
