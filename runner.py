import subprocess
import time

# Define the scripts to run
scripts = {
    'dash': 'python3 Helper/dash.py',
    #'server': 'python3 Experimental/server.py',
    #'speed': 'python3 Experimental/speed.py'
}

# Dictionary to hold process references
processes = {}

def start_scripts():
    global processes
    for name, command in scripts.items():
        print(f"Starting {name}...")
        process = subprocess.Popen(command, shell=True)
        processes[name] = process
        print(f"{name} started with PID {process.pid}")

def stop_scripts():
    global processes
    for name, process in processes.items():
        print(f"Stopping {name} with PID {process.pid}...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"{name} did not terminate gracefully. Killing...")
            process.kill()
        print(f"{name} stopped")

def main():
    start_scripts()
    
    try:
        # Keep the script running to monitor or interact with it
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        stop_scripts()
    except Exception as e:
        print(f"An error occurred: {e}")
        stop_scripts()

if __name__ == "__main__":
    main()
