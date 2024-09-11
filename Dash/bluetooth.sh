#!/bin/bash

# Log file
LOGFILE="install_log.txt"
SCAN_PID_FILE="scan.pid"

# Function to log output and errors
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOGFILE
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

# Select Bluetooth device
select_bluetooth_device

log "Bluetooth device set. Please restart Raspberry Pi."