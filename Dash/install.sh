#!/bin/bash

# Log file
LOGFILE="install_log.txt"
SCAN_PID_FILE="scan.pid"

# Function to log output and errors
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOGFILE
}

# Function to handle errors and undo changes
error_exit() {
    log "Error occurred. Undoing changes..."
    # Add any cleanup/undo commands here
    if [ -d "/home/pi/.config/autostart" ]; then
        mv /home/pi/.config/autostart/boot.desktop ./boot.desktop 2>>$LOGFILE
    fi
    deactivate 2>/dev/null
    rm -rf env 2>>$LOGFILE
    log "Installation failed. Exiting."
    exit 1
}

# Function to handle Bluetooth device selection
select_bluetooth_device() {
    log "Scanning for Bluetooth devices..."

    # Start Bluetooth scan in the background
    bluetoothctl scan on > /dev/null 2>&1 &
    echo $! > $SCAN_PID_FILE  # Save PID of the scan process

    # Prompt user to cancel scan or wait
    echo "Press 'c' to cancel the scan or wait for the scan to complete."

    # Wait for user input or scan completion
    timeout=15
    while [ $timeout -gt 0 ]; do
        read -t 1 -n 1 user_input
        if [[ "$user_input" == "c" ]]; then
            log "Cancelling Bluetooth scan..."
            kill $(cat $SCAN_PID_FILE) 2>/dev/null
            rm -f $SCAN_PID_FILE
            echo "Scan cancelled."
            mac_address="No Bluetooth"
            break
        fi
        timeout=$((timeout - 1))
    done

    # Stop the scan if it was not manually cancelled
    if [ -f $SCAN_PID_FILE ]; then
        log "Stopping Bluetooth scan..."
        kill $(cat $SCAN_PID_FILE) 2>/dev/null
        rm -f $SCAN_PID_FILE
    fi

    # List available devices
    devices=$(bluetoothctl devices)
    if [ -z "$devices" ] && [ "$mac_address" != "No Bluetooth" ]; then
        log "No devices found or scanning failed."
        echo "No devices found or scanning failed. Exiting." >&2
        exit 1
    fi

    log "Available Bluetooth devices:"
    
    # Display devices with numbers
    i=1
    declare -A device_list
    while IFS= read -r line; do
        if [[ $line =~ ^Device\ (.*)\ (.*) ]]; then
            mac_address=${BASH_REMATCH[1]}
            device_name=${BASH_REMATCH[2]}
            device_list[$i]=$mac_address
            echo "$i) $device_name ($mac_address)"
            ((i++))
        fi
    done <<< "$devices"

    # Add option for no Bluetooth
    echo "$i) No Bluetooth"

    while true; do
        # Prompt user to select device by number or enter MAC address manually
        read -p "Enter the number of the device you want to use (or type 'manual' to enter it manually): " user_input

        if [[ "$user_input" == "manual" ]]; then
            read -p "Enter the MAC address manually (format XX:XX:XX:XX:XX:XX): " mac_address
            if [[ ! "$mac_address" =~ ^[0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5}$ ]]; then
                log "Invalid MAC address format. Please enter a valid MAC address."
                echo "Invalid MAC address format. Please enter a valid MAC address."
                continue
            fi
            break
        elif [[ "$user_input" =~ ^[0-9]+$ ]] && [[ "$user_input" -ge 1 ]] && [[ "$user_input" -lt "$i" ]]; then
            mac_address=${device_list[$user_input]}
            break
        elif [[ "$user_input" -eq "$i" ]]; then
            mac_address="No Bluetooth"
            break
        else
            log "Invalid selection. Please enter a valid number from the list or 'manual'."
            echo "Invalid selection. Please enter a valid number from the list or 'manual'."
        fi
    done

    log "Selected MAC address: $mac_address"
    echo "$mac_address" > /home/pi/Dash/Data/device.txt
    log "MAC address saved to /home/pi/Dash/Data/device.txt"
}

# Start installation
log "Starting installation..."

# Update package lists and install Bluetooth packages
log "Updating package lists and installing Bluetooth packages..."
sudo apt update >> $LOGFILE 2>&1
if sudo apt install -y bluetooth pi-bluetooth bluez >> $LOGFILE 2>&1; then
    log "Bluetooth packages installed successfully."
else
    log "Failed to install Bluetooth packages."
    error_exit
fi

# Make sure boot.sh and boot.desktop are executable
chmod +x boot.sh boot.desktop
log "Made boot.sh and boot.desktop executable."

# Creating autostart directory if it doesn't exist
log "Checking for autostart directory"
if [ ! -d /home/pi/.config/autostart ]; then
    log "Autostart directory does not exist. Creating directory..."
    mkdir -p /home/pi/.config/autostart
    if [ $? -ne 0 ]; then
        log "Failed to create autostart directory. Exiting."
        exit 1
    fi
fi

# Moving autostart app
log "Creating autostart app"
if mv boot.desktop /home/pi/.config/autostart/ 2>>$LOGFILE; then
    log "Autostart app created."
else
    error_exit
fi

# Creating virtual environment
log "Creating virtual environment"
if python3 -m venv env 2>>$LOGFILE; then
    log "Virtual environment created."
else
    error_exit
fi

# Activating virtual environment
log "Activating virtual environment"
source env/bin/activate 2>>$LOGFILE
if [ $? -eq 0 ]; then
    log "Virtual environment activated."
else
    error_exit
fi

# Changing brightness permissions
log "Changing brightness permissions"
sudo chown pi /sys/class/backlight/10-0045/brightness >> $LOGFILE
if [ $? -eq 0 ]; then
    log "Ownership of brightness file changed."
else
    error_exit
fi

# Granting brightness permissions
log "Granting brightness permissions"
sudo chmod 666 /sys/class/backlight/10-0045/brightness >> $LOGFILE
if [ $? -eq 0 ]; then
    log "Permissions of brightness file granted."
else
    error_exit
fi

# Adding visudo entry for rfcomm without password
log "Adding visudo entry for rfcomm"
VISUDO_LINE="pi ALL=(ALL) NOPASSWD: /usr/bin/rfcomm"
sudo grep -qF "$VISUDO_LINE" /etc/sudoers || echo "$VISUDO_LINE" | sudo EDITOR='tee -a' visudo
if [ $? -eq 0 ]; then
    log "Visudo entry added successfully for rfcomm."
else
    error_exit
fi

# Installing requirements
log "Installing requirements"
if pip install -r requirements.txt 2>>$LOGFILE; then
    log "Requirements installed."
else
    error_exit
fi

# Select Bluetooth device
select_bluetooth_device

log "Done installing. Please restart Raspberry Pi."
