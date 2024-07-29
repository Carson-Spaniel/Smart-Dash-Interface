import requests
import json
import time

while True:
    # Define the URL for the POST request
    url = "http://127.0.0.1:5000/speed"

    # Define the headers, specifying that we're sending JSON data
    headers = {
        "Content-Type": "application/json"
    }

    lat = 30.669233
    lon = -97.681279

    # Define the data payload as a Python dictionary
    data = {
        "lat": lat,
        "lon": lon
    }

    # Convert the dictionary to a JSON string
    json_data = json.dumps(data)

    try:
        # Send the POST request
        response = requests.post(url, headers=headers, data=json_data)
    
        with open("Data/speed_limit.txt", "w") as file:
            file.write(str(response.json()['data']['speed_limit']))

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    
    finally:
        time.sleep(5)