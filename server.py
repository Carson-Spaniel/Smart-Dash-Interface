from flask import Flask, jsonify, request
import os
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

    response = {
        "message": "Speed limit retrieved successfully",
        "data": {
            "speed_limit": round(random.randint(5,85) / 5) * 5
        }
    }

    return jsonify(response), 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
