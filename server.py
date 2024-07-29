from flask import Flask, jsonify, request
import random

# Create a Flask application instance
app = Flask(__name__)

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

    # Process the data (e.g., save to a database, perform calculations, etc.)
    # For now, we'll just echo the received data
    response = {
        "message": "Data received successfully",
        "data": {
            "speed": round(random.randint(5,85) / 5) * 5
        }
    }

    # Return a JSON response with status code 201
    return jsonify(response), 201

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
