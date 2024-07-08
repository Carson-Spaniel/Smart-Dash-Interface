# Path to the brightness file
brightness_file = "/sys/class/backlight/10-0045/brightness"

def get_brightness():
    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        return current_brightness
    except Exception as e:
        print(f"Error increasing brightness: {e}")
        return 0
    
BRIGHTNESS = get_brightness()

# Function to adjust brightness
def adjust_brightness(value):
    global BRIGHTNESS
    BRIGHTNESS = value
    try:
        with open(brightness_file, "w") as file:
            file.write(str(value))
        print(f"Brightness adjusted to {value}")
        
    except Exception as e:
        print(f"Error adjusting brightness: {e}")

# Function to decrease brightness
def decrease_brightness():
    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        new_brightness = max(current_brightness - 15, 0)  # Ensure brightness doesn't go below 10
        adjust_brightness(new_brightness)
    except Exception as e:
        print(f"Error decreasing brightness: {e}")

# Function to increase brightness
def increase_brightness():
    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        new_brightness = min(current_brightness + 15, 255)  # Adjust 20 to your desired increment
        adjust_brightness(new_brightness)
    except Exception as e:
        print(f"Error increasing brightness: {e}")

# Function to save max horsepower data to a file
def save_rpm(RPM_MAX, SHIFT):
    with open("Data/RPM.txt", "w") as file:
        file.write(f"{RPM_MAX},{SHIFT}")

# Function to load max horsepower data from a file
def load_rpm():
    try:
        with open("Data/RPM.txt", "r") as file:
            data = file.read().split(",")
            max = int(data[0])
            shift = int(data[1])
    except Exception as e:
        print(e)
        max = 8000
        shift = 6500

    return max, shift

# Function to calculate MPG
def calculate_mpg(speed, maf):
    """
    Calculate miles per gallon (MPG) based on vehicle speed and mass air flow (MAF).
    
    Parameters:
    speed (float): Vehicle speed in miles per hour.
    maf (float): Mass air flow in grams per second.
    
    Returns:
    float: Calculated MPG.
    """
    if speed == 0 or maf == 0:
        return 0
    
    # Convert MAF from grams per second to grams per hour
    maf_gph = maf * 3600

    # Convert grams per hour to pounds per hour (1 pound = 453.592 grams)
    maf_pph = maf_gph / 453.592

    # Convert pounds per hour to gallons per hour (1 gallon of gasoline = 6.17 pounds)
    gph = maf_pph / 6.17

    # Calculate MPG
    mpg = speed / gph

    return round(mpg*10, 1)