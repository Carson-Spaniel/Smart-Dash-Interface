#!/bin/bash

logfile=/home/pi/Dash/bootup.log
device=/home/pi/Dash/Data/device.txt

echo "----------Starting boot.sh----------" > $logfile

echo "----------Setting environment variables----------" >> $logfile
# Set the DISPLAY variable
export DISPLAY=:0

echo "----------Changing brightness permissions----------" >> $logfile
# Change permissions
sudo chown pi /sys/class/backlight/10-0045/brightness >> $logfile

echo "----------Granting brightness permissions----------" >> $logfile
# Grant write permission
sudo chmod 666 /sys/class/backlight/10-0045/brightness >> $logfile

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
        break
    elif grep -q "Restarting script" $logfile; then
        echo "----------Restarting dash script----------" >> $logfile
        continue
    else
        break
    fi
done

echo "----------Deactivating virtual environment----------" >> $logfile
# Deactivate the virtual environment when script finishes
deactivate >> $logfile
