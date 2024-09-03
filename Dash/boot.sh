#!/bin/bash

logfile=/home/pi/Dash/bootup.log
device=/home/pi/Dash/Data/device.txt

# Path to the wifi.txt file
WIFI_STATUS_FILE="/home/pi/Dash/Data/wifi.txt"

# Ensure the wifi.txt file exists
if [ ! -f "$WIFI_STATUS_FILE" ]; then
    echo "0" > "$WIFI_STATUS_FILE"  # Initialize the file with 0
fi

# Function to constantly check Wi-Fi status by pinging an external server
check_wifi_loop() {
    while true; do
        # Ping an external server (e.g., Google's DNS server) to check internet connectivity
        if ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
            # Internet is accessible, write 1 to the file
            echo "1" > "$WIFI_STATUS_FILE"
        else
            # Internet is not accessible, write 0 to the file
            echo "0" > "$WIFI_STATUS_FILE"
        fi

        # Wait for 10 seconds before the next check (adjust as needed)
        sleep 10
    done
}

# Start Wi-Fi checker only if not already running
if ! pgrep -f check_wifi_loop > /dev/null; then
    check_wifi_loop &
fi

echo "----------Starting boot.sh----------" > $logfile

echo "----------Setting environment variables----------" >> $logfile
# Set the DISPLAY variable
export DISPLAY=:0

echo "----------Creating bluetooth port----------" >> $logfile

# Read the Bluetooth MAC address from the file
if [ -f "$device" ]; then
    bt_mac=$(cat $device)
    if [ "$bt_mac" == "No Bluetooth" ]; then
        echo "No Bluetooth configured. Skipping Bluetooth setup." >> $logfile
    elif [ -n "$bt_mac" ]; then
        # Create the Bluetooth Port
        sudo rfcomm bind /dev/rfcomm0 "$bt_mac" >> $logfile
        echo "Using Bluetooth address: $bt_mac" >> $logfile
    else
        echo "Invalid entry in $device. Exiting." >> $logfile
        exit 1
    fi
else
    echo "Device file $device not found. Exiting." >> $logfile
    exit 1
fi

echo "----------Moving to correct directory----------" >> $logfile
# Move into correct folder
cd /home/pi/Dash/

echo "----------Activating virtual environment----------" >> $logfile
# Activate the virtual environment
source env/bin/activate >> $logfile

echo "----------Starting dash script----------" >> $logfile
while true; do
    # Run your Python script in a loop
    python3 ./dash.py >> $logfile

    # Check if the script needs to be restarted
    if grep -q "Exiting..." $logfile; then
        echo "----------Ending dash script----------" >> $logfile
        sudo shutdown -h now
        break
    elif grep -q "Restarting script" $logfile; then
        echo "----------Restarting dash script----------" >> $logfile
        continue
    elif grep -q "Wifi Update" $logfile; then
        echo "----------Updating through Wifi----------" >> $logfile
        cd /home/pi/
        wget -O Dash.tar.xz https://github.com/Carson-Spaniel/Smart-Dash-Interface/releases/latest/download/Dash.tar.xz
        tar -xJvf Dash.tar.xz
        cd Dash/
        # Activating virtual environment
        echo "Activating virtual environment" >> $logfile
        source env/bin/activate 2>>$logfile

        # Installing requirements
        log "Installing requirements"
        if pip install -r requirements.txt 2>>$logfile; then
            echo "Requirements installed." >> $logfile
        else
            break
        fi
        continue
    else
        break
    fi
done

echo "----------Deactivating virtual environment----------" >> $logfile
# Deactivate the virtual environment when script finishes
deactivate >> $logfile