#!/bin/bash

logfile=~/bootup.log

echo "----------Starting boot.sh----------" > $logfile

echo "----------Setting environment variables----------" >> $logfile
# Set the DISPLAY variable
export DISPLAY=:0

echo "----------Changing brightness permissions----------" >> $logfile
# Change permissions (replace <username> with your actual username)
sudo chown pi /sys/class/backlight/10-0045/brightness >> $logfile

echo "----------Granting brightness permissions----------" >> $logfile
# Grant write permission
sudo chmod 666 /sys/class/backlight/10-0045/brightness >> $logfile

echo "----------Creating bluetooth port----------" >> $logfile
# Create the Bluetooth Port
sudo rfcomm bind /dev/rfcomm0 8C:DE:52:DC:17:24 >> $logfile

echo "----------Moving to correct directory----------" >> $logfile
# Move into correct folder
cd /home/pi/Python-OBD-Practice/

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
