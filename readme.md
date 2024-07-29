# Smart Dash Interface

This Python script creates a Smart Dash Pygame interface for a landscape 4.3-inch display. It utilizes Pygame for graphics rendering and OBD-II for vehicle data retrieval.

## Requirements

- Python 3.x
- A Bluetooth OBD-II adapter

## Installation

1. Install Python (if not already installed).
2. Install Requirements: `pip install -r requirements.txt`
3. Ensure you have a Bluetooth OBD-II adapter paired with your device.

## Usage

1. Clone or download the repository.
2. Connect your Bluetooth OBD-II adapter to your vehicle.
3. Run the script: `python dash.py`
4. The script will display a Smart Dash interface on your screen.

## Features

- **Main Page**:
  - Displays real-time vehicle data such as RPM, speed, voltage, fuel level, ambient temperature, and MPG.
  - Shift lights.
  - Clickable buttons to navigate to other pages.
  
- **Settings Page**:
  - Option to flip the display vertically (to act as a Heads Up Display).
  - Brightness adjustment.
  - Shift light.
  - Exit button.

- **RPM Page**:
  - Allows adjustment of RPM_MAX and SHIFT values.
  - RPM gauge with shift indicator.

- **Error Code Page**:
  - Allows for reading and clearing of Check Engine Light codes.

- **Chevrolet Logo Animation**:
  - Displayed on startup (can be disabled for non-DEV mode).

## Configuration

- **Environment Variables**:
  - `PI`: Set to `True` if running on Raspberry Pi with Bluetooth, `False` for other platforms.

- **Fonts**:
  - The script uses digital-7.ttf font for text rendering. Ensure it's in the correct directory or update font paths.

- **Bluetooth Connection**:
  - Configure the correct port for the Bluetooth connection (`port = "/dev/rfcomm0"` for Raspberry Pi, `"COM5"` for Windows).

## Additional Notes

- The script simulates data in `DEV` mode. Ensure to connect a Bluetooth OBD-II adapter in production mode.
- A Bluetooth OBD-II adapter makes it cleaner, but it will also work with a wired setup.
- Feel free to customize fonts, colors, and layout as needed in the script.
