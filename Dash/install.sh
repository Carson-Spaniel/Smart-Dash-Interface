#!/bin/bash

echo "Installing..."

sudo mv boot.desktop ~/.config/autostart -y # Make it run at start
python3 -m venv env # Create virtual environment
source env/bin/activate # Activate the virtual environment
pip install -r requirements.txt # Install requirements

echo "Done installing. Please Restart Raspberry Pi."