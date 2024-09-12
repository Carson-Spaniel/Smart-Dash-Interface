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

# Install X server and startx (X Window System)
log "Installing X server and startx..."
if sudo apt install -y --no-install-recommends xserver-xorg xinit >> $LOGFILE 2>&1; then
    log "X server and startx installed successfully."
else
    log "Failed to install X server and startx."
    error_exit
fi

# Create ~/.xinitrc file with sudo and a here document
log "Creating ~/.xinitrc file..."
sudo bash -c 'cat <<EOF > /home/pi/.xinitrc
#!/bin/sh
cd /home/pi/Dash
./boot.sh &
exec openbox-session
EOF'

# Change permissions for the ~/.xinitrc file
sudo chmod +x /home/pi/.xinitrc
log "~/.xinitrc file created and made executable."

# Modify ~/.bashrc to start X at boot
log "Configuring startx to run at boot..."
if grep -q 'startx' /home/pi/.bashrc; then
    log ".bashrc already configured."
else
    echo 'if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then cd /home/pi/Dash/ && startx ./boot.sh; fi' >> /home/pi/.bashrc
    log ".bashrc configured to start X at boot."
fi

# Configure auto-login on tty1
log "Configuring auto-login for the pi user on tty1..."
if [ ! -d /etc/systemd/system/getty@tty1.service.d ]; then
    sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
fi

sudo bash -c 'cat <<EOF > /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I \$TERM
EOF'

sudo systemctl daemon-reload
log "Auto-login configured successfully."

cd /home/pi/

log "Downloading and installing Brightness tools..."
wget https://files.waveshare.com/upload/f/f4/Brightness.zip >> $LOGFILE 2>&1
if [ $? -eq 0 ]; then
    log "Brightness tools downloaded."
else
    log "Failed to download Brightness tools."
    error_exit
fi

unzip Brightness.zip >> $LOGFILE 2>&1
if [ $? -eq 0 ]; then
    log "Brightness tools unzipped."
else
    log "Failed to unzip Brightness tools."
    error_exit
fi

cd Brightness
sudo chmod +x install.sh
if ./install.sh >> $LOGFILE 2>&1; then
    log "Brightness tools installed."
else
    log "Failed to install Brightness tools."
    error_exit
fi

cd /home/pi/Dash

# Create virtual environment
log "Creating virtual environment..."
if python3 -m venv env 2>>$LOGFILE; then
    log "Virtual environment created."
else
    error_exit
fi

# Activate virtual environment
log "Activating virtual environment..."
source env/bin/activate 2>>$LOGFILE
if [ $? -eq 0 ]; then
    log "Virtual environment activated."
else
    error_exit
fi

# Changing brightness permissions
log "Changing brightness permissions..."
sudo chown pi /sys/class/backlight/10-0045/brightness >> $LOGFILE
if [ $? -eq 0 ]; then
    log "Ownership of brightness file changed."
else
    error_exit
fi

# Granting brightness permissions
log "Granting brightness permissions..."
sudo chmod 666 /sys/class/backlight/10-0045/brightness >> $LOGFILE
if [ $? -eq 0 ]; then
    log "Permissions of brightness file granted."
else
    error_exit
fi

# Adding visudo entry for rfcomm without password
log "Adding visudo entry for rfcomm..."
VISUDO_LINE="pi ALL=(ALL) NOPASSWD: /usr/bin/rfcomm"
sudo grep -qF "$VISUDO_LINE" /etc/sudoers || echo "$VISUDO_LINE" | sudo EDITOR='tee -a' visudo
if [ $? -eq 0 ]; then
    log "Visudo entry added successfully for rfcomm."
else
    error_exit
fi

# Installing requirements
log "Installing requirements..."
if pip install -r requirements.txt 2>>$LOGFILE; then
    log "Requirements installed."
else
    error_exit
fi

log "Done installing. Please restart Raspberry Pi."
