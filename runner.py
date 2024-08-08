import subprocess
import time
import threading
import os
import requests

# Define the scripts to run
scripts = {
    'dash': 'python3 Helper/dash.py',
    'server': 'python3 Experimental/server.py',
    'speed': 'python3 Experimental/speed.py'
}

stop = False

# Dictionary to hold process references
processes = {}

def start_scripts():
    global processes, stop

    with open('Data/kill.txt', 'w') as file:
        file.write(str(0))

    for name, command in scripts.items():
        print(f"Starting {name}...")
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        processes[name] = process
        print(f"{name} started with PID {process.pid}")
        time.sleep(1)

def stop_scripts():
    global stop
    stop = True
    with open('Data/kill.txt', 'w') as file:
        file.write(str(1))

    # Define the URL to end flask app
    url = "http://127.0.0.1:5000/shutdown"

    try:
        # Send the end request
        response = requests.post(url)
    
        if response.status_code == 200:
            print('End flask signal received.')

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def monitor_dash():
    global processes, stop
    dash_process = processes.get('dash')
    if dash_process:
        while dash_process.poll() is None:
            # Wait for a bit before checking again
            time.sleep(1)
        print("dash.py has stopped. Terminating other scripts...")
        stop = True
        stop_scripts()

def main():
    start_scripts()
    
    try:
        # Start monitoring `dash.py` in a separate thread
        monitor_thread = threading.Thread(target=monitor_dash)
        monitor_thread.start()
        
        # Keep the script running to monitor or interact with it
        while not stop:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        stop_scripts()
    except Exception as e:
        print(f"An error occurred: {e}")
        stop_scripts()

if __name__ == "__main__":
    main()