# Smart Dash Interface

This Python script creates a Smart Dash Pygame interface for a landscape 4.3-inch display. It utilizes Pygame for graphics rendering and OBD-II for vehicle data retrieval.

## Contributions

We welcome and appreciate any contributions to improve the Smart Dash Interface! Whether it’s reporting issues, suggesting new features, or submitting pull requests, your input helps make the project better for everyone.

Feel free to fork the repository, open issues, or start a discussion. We encourage collaboration and are excited to see what you bring to the project!

## Needs

- A Bluetooth OBD-II adapter.

## Raspberry Pi Installation

### You can find all these commands in [Download Script](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/download.sh)
1. Move into the home directory with `cd /home/pi/`.
2. Run `wget -O Dash.tar.xz https://github.com/Carson-Spaniel/Smart-Dash-Interface/releases/latest/download/Dash.tar.xz` to download the files.
3. Run `tar -xJvf Dash.tar.xz` to unpack everything.
4. Change into the Dash directory using `cd Dash/`.
5. Run `sudo ./install.sh` to start the installation and connection with your Bluetooth device.
6. Ensure you have a Bluetooth OBD-II adapter paired with your device and put into either the `boot.sh` script (Bluetooth connection) or `dash.py` script.
7. Reboot your raspberry pi.

## Features

- **Main Page**:

  ![Main Page Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/Main.png)
  
  ![Main Page with Optimize On Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/Optimize.png) (Optimize on)
  - Displays real-time vehicle data such as RPM, speed, voltage, fuel level, ambient temperature, and MPG.
  - Shift lights.
  - Clickable buttons to navigate to other pages.

- **Customization Page**

  ![Customization Settings Page Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/Customize.png)

  - Change font color.
  - Change Background 1 color: RPM and Fuel level background.
  - Change Background 2 color: Main background.
  - Change Background Image. 

- **Shift Light Customization Page**

  ![Shift Light Settings Page Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/Shift.png)

  - Shift light toggle.
  - Shift light color 1: First color to appear in shift sequence.
  - Shift light color 2: Second color to appear in shift sequence.
  - Shift light color 3: Third color to appear in shift sequence.
  - Shift light color 4: Fourth and blinking color to appear in shift sequence.
  - Shift Starting RPM: Where the lights start to turn on.

- **General Settings Page**:

  ![General Settings Page Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/General.png)
  - Option to flip the display vertically (to act as a Heads Up Display).
  - Brightness adjustment.
  - Delay readings: Slow down all readings to happen at the same time.
  - Optimize readings: Only read RPM and Fuel level data.

- **RPM Settings Page**:

  ![RPM Settings Page Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/RPM.png)

  - Allows adjustment of RPM_MAX and SHIFT values.

- **System Settings Page**:

  ![System Settings](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/System.png)

  - Version.
  - Wifi update: Be able to update the system when connected to wifi.

- **Trouble Code Page**:

  ![Trouble Code Page Screenshot](https://github.com/Carson-Spaniel/Smart-Dash-Interface/blob/main/Screenshots/Trouble.png)
  - Allows for reading and clearing of Check Engine Light codes.

- **Chevrolet Camaro Logo Animation**:
  - Displayed on startup (can be changed in the code).

## Configuration

- **Environment Variables**:
  - `DEV`: Set to `True` if testing, `False` if running with a connection to the car.
  - `PI`: Set to `True` if running on Raspberry Pi with Bluetooth, `False` for other platforms.

- **Fonts**:
  - The script uses digital-7.ttf font for text rendering. Ensure it's in the correct directory or update font paths.

- **Bluetooth Connection**:
  - Configure the correct port for the Bluetooth connection (`port = "/dev/rfcomm0"` for Raspberry Pi, `"COM5"` for Windows).

## Items List
- [Raspberry Pi 4 Model B](https://www.amazon.com/Raspberry-Model-2019-Quad-Bluetooth/dp/B07TC2BK1X/ref=sr_1_1?crid=2BYNDBGLENAC5&dib=eyJ2IjoiMSJ9._PqCjKFXecURzDfuwZg7dnSe-rn341n1YEUC3kxkYF-fUtGzxgoMMPWaAILcn0KOAk9GBqVxr0qMogiZ0hanIqy5fR2zahX1IITuSesTy7IeXEuWiWbtfjlO2WnfbhDOJijqyRA6b1dW__aL7P3GIR-EdczlNudnAYbhFope4fqo2Q9yVhmqmUEm0phh1Md91q1SKzmfvBCGbQbmJx9gIjg_rjtShxjMSWl1p7gtT49lYMelpwEAaVOOC-unZja2v2CHsWKokxWj2CcMSekV-h9E5p_7LKkBuQDeRHcLHNk.--3ONeF3E3njn6i4GFKc_EO_06h6CLneroWD_nEM2rI&dib_tag=se&keywords=raspberry%2Bpi%2B4b&qid=1724778256&s=electronics&sprefix=rasberry%2Bpi%2B4b%2Celectronics%2C129&sr=1-1&th=1)
- [4.3inch DSI Touchscreen LCD Display with Case for Raspberry Pi 4B](https://www.amazon.com/dp/B09B29T8YF/?coliid=IXOU52HY9KKDL&colid=3DH0CV6R3JLCG&ref_=list_c_wl_lv_ov_lig_dp_it&th=1)
- [Bluetooth OBD II Scanner](https://www.amazon.com/Veepeak-OBDCheck-Bluetooth-Diagnostic-Supports/dp/B073XKQQQW/ref=sr_1_2?crid=2TKSEUFTYTC0J&dib=eyJ2IjoiMSJ9.cDU5tykXBvNKabKDav9eh5h5Qbph9bgA5-QG0BN5lTpuN1Ud5sjlaOt3HjeilOAJjSZgB82fUeHNj5DBdSesmlkaLE5y21QmGkhW6-TQWs_roTX6A8kNwkImi6C_zYqbL9K-Jfei9IqlR02fezhNF9okMUYdS9d23rLWG4gGrHNUt_kydlCzeDboiAO8bTlw5Djb4s3wppV9fPohEpu4suO2ODDZB2mqncf3-ZIEt5tm5kw2hWVNcI9yipuRDSPXBtXx9N4kSMvNCq8tQcaI0owKePp1eIyxNWevf2xsGQ4.vz9kAGDDxcmWIAAc3c8dC6pOX_AT30D2pvrI-MXQH6A&dib_tag=se&keywords=elm+327+obd2+scanner+bluetooth&qid=1724778387&sprefix=elm+%2Caps%2C148&sr=8-2)

## Additional Notes

- The script simulates data in `DEV` mode. Ensure to connect a Bluetooth OBD-II adapter in production mode.
- A Bluetooth OBD-II adapter makes it cleaner, but it will also work with a wired setup.
- Any Raspberry Pi should work but just make sure you have Bluetooth unless running a wired connection.
- Feel free to customize fonts, colors, and layout as needed in the script.

## Upcoming
- Performance page: top speed tracking, 0-60 time tracking, more performance related things. Will include a graph of Speed and RPM over Time.
- Bluetooth setting: Add Bluetooth connection from the dash interface.
- Update readme: Update the readme to the most current version.
- Main displays: Add different looks for the main page.

## Far Future
- Raspberry Pi hotspot for wifi connection to phone for GPS data for GPS related features.

## Versions

### v2.7.0
- Added
  - Development Mode: Going to have a page of settings that can help you fine tune your dash. Can be turned on in the system settings. 
  - Backgrounds: More backgrounds to choose from.
  - Documentation: Large amounts of comments for each function.
- Updated
  - Code structure: Sorted most things into different functions and files making it easier to find where things are at.
  - Rendering: Optimized code to render each frame faster.
  - Blink pattern: Blinks based on time rather than internal clock.
- Removed
  - Background: Removed background `6.jpg` because it was causing slow downs when loading each frame.

### v2.6.2
- Updated
  - Queries: Speeding up queries.  

### v2.6.1
- Updated
  - Wifi Updating: Cleans its self up after downloading. Can revert if the download doesn't go correctly.  

### v2.6.0
- Added
  - Backgrounds: You can now customize the background with different pictures.
- Updated
  - Queries: Optimized queries to only run when needed to reduce CPU usage.

### v2.5.0
- Added
  - Query check: Checks to see if your car supports the command its about to call to reduce errors.
- Updated
  - OBD-II Connection: Made it so you can load into the dash without needing to connect. While not connected, it tries reconnecting every few seconds.

### v2.4.1
- Updated
  - Shift Light padding: Renamed to "Shift Starting RPM." Displays the point at which the lights start to turn on.
  - Install script: Added a part to install bluetooth stuff.
- Added
  - Bluetooth script: Run this to find bluetooth devices.

### v2.4.0
- Added
  - Shift Light Settings: Can now change the colors of the shift light as well as adjust the "padding" which is how you control when the lights start turing on.

### v2.3.2
- Updated
  - Colors: Much more colors have been added.

### v2.3.1
- Fixed
  - Wifi Update: Some problems associated with old code.
  - Exiting: Shutdown was encountering an error.

### v2.3.0
- Added
  - Color Customization: Can now change the colors of the font and backgrounds.

### v2.2.0
- Added
  - Wifi Update: Be able to update the device over wifi.

### v2.1.2
- Fixed
  - Install script bug: Wouldn't let you pick a number from the bluetooth list.

### v2.1.1
- Fixed
  - Install scripts: Trying to make it even easier with as little interaction as possible.

### v2.1.0
- Added
  - Customization Page: Added customization page that will be used to customize the overall look of the dash.

### v2.0.0
- Added
  - Versioning: Implemented versions for future updates.
  - Swiping gestures: Can now swipe on the screen rather than pressing hard to press buttons.
- Changed
  - Overall page layout: Changed to a 2D format to more categorize pages.

### v1.x.x 
- All previous versions were not documented.
- This is where the current readme is at.
