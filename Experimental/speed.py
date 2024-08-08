import requests
import json
import time
import gpsd
import os
import serial

# Path to the GPS data file
gps_data_file = 'Data/gps_data.txt'

# Function to initialize GPS with last known data
def initialize_gps():
    if os.path.exists(gps_data_file):
        with open(gps_data_file, 'r') as file:
            data = file.read().strip().split(',')
            if len(data) == 3:
                timestamp, lat, lon = data
                # Format latitude and longitude as NMEA sentences expect
                nmea_lat = f"{float(lat):.6f}"
                nmea_lon = f"{float(lon):.6f}"
                nmea_sentence = f"$GPGGA,{timestamp},{nmea_lat},N,{nmea_lon},E,1,08,0.9,545.4,M,46.9,M,,*47"
                # Send NMEA sentence to the GPS module (adjust the serial port if needed)
                with serial.Serial('/dev/serial0', 38400, timeout=1) as ser:
                    ser.write((nmea_sentence + '\r\n').encode('utf-8'))
                print(f"Initialized GPS with data: {timestamp}, {lat}, {lon}")

# Initialize the GPS with last known data
initialize_gps()

# Connect to the local gpsd
gpsd.connect()

stop = False

while not stop:
    with open('Data/kill.txt', 'r') as file:
        stop = int(file.readline())

    try:
        packet = gpsd.get_current()
    except Exception:
        print('passing')
        time.sleep(2)
        continue

    # Define the URL for the POST request
    url = "http://127.0.0.1:5000/speed"

    # Define the headers, specifying that we're sending JSON data
    headers = {
        "Content-Type": "application/json"
    }

    #lat, lon = 30.681598416806178, -97.7147931842906
    lat = packet.lat
    lon = packet.lon

    if lat and lon:

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

            # Log the current GPS data to the file
            with open(gps_data_file, 'w') as file:
                file.write(f"{packet.time},{lat},{lon}\n")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        time.sleep(5)

print('speed.py has ended.')