import obd
import time
import os
from math import pi
from .builder import *

# Path to the brightness file
brightness_file = "/sys/class/backlight/10-0045/brightness"

def try_connect(DEV):
    """
    Attempts to establish a connection to the OBD-II adapter via Bluetooth, unless development mode is enabled.

    Args:
        DEV (bool): A flag indicating whether development mode is on. 
                    If True, no connection to the car will be made, and simulated data will be used. 
                    If False, the function will attempt to connect to the OBD-II adapter.

    Description:
        - In development mode (`DEV=True`), the function skips the connection process, assuming simulated data is being used.
        - If not in development mode (`DEV=False`), the function tries to connect to the OBD-II adapter using the "/dev/rfcomm0" port on a Raspberry Pi.
        - Once connected, it checks if supported PIDs (Parameter IDs) are already loaded.
        - If supported PIDs are not loaded, the function queries the OBD-II adapter for the supported PIDs (commands A, B, and C).
        - The results from the adapter are converted into binary strings to identify supported PIDs, which are then saved for later use.
        - The connection is retried up to 3 times if it fails.

    Global Variables:
        connect (bool): Indicates if the connection to the OBD-II adapter was successful.
        connection (obd.OBD): The connection object representing the OBD-II connection.
        supported (list): List of supported PIDs retrieved from the OBD-II adapter.

    Exceptions:
        - Catches and prints any exceptions that occur during the connection attempt.
        - Prints an error message if the connection fails after multiple attempts.
    """

    global connect, connection, supported
    if not DEV:
        for i in range(3):
            try:
                print('\nAttempting to connect...\n')

                # The Bluetooth port for RFCOMM on Raspberry Pi
                port = "/dev/rfcomm0"
                    
                # Connect to the OBD-II adapter
                connection = obd.OBD(portstr=port)

                # Print a message indicating connection
                if connection.is_connected():
                    print("Connected to OBD-II adapter. Turning on display.")

                    supported = load_supported()

                    if len(supported) == 0:
                        # Query the supported PIDs for different ranges
                        supported_response_a = connection.query(obd.commands.PIDS_A)
                        supported_response_b = connection.query(obd.commands.PIDS_B)
                        supported_response_c = connection.query(obd.commands.PIDS_C)

                        # Initialize an empty string for the combined binary string
                        combined_binary_string = ""

                        # Convert each supported response to a binary string and concatenate
                        if supported_response_a.value:
                            bit_array_a = supported_response_a.value
                            binary_string_a = ''.join(str(int(bit)) for bit in bit_array_a)
                            combined_binary_string += binary_string_a  # Append A's binary string
                        
                        if supported_response_b.value:
                            bit_array_b = supported_response_b.value
                            binary_string_b = ''.join(str(int(bit)) for bit in bit_array_b)
                            combined_binary_string += binary_string_b  # Append B's binary string
                        
                        if supported_response_c.value:
                            bit_array_c = supported_response_c.value
                            binary_string_c = ''.join(str(int(bit)) for bit in bit_array_c)
                            combined_binary_string += binary_string_c  # Append C's binary string

                        # Loop through each bit and check if the PID is supported
                        for i, bit in enumerate(combined_binary_string):
                            pid_number = i + 1  # PIDs start from 1
                            if bit == '1':
                                supported.append(f"0x{pid_number:02X}")

                        save_supported(supported)
                    
                    connect = True
                    break
                else:
                    print("Could not connect to OBD-II adapter.")
            except Exception as e:
                print(e)
                print('An error occurred.')

def get_brightness():
    """
    Retrieves the current screen brightness from the specified file.

    Returns:
        int: The current brightness value if successful, or 0 if an error occurs.

    Description:
        - Opens the brightness file and reads the current brightness value.
        - If there's an error (e.g., file not found or permission issues), it prints an error message and returns 0.
    """

    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        return current_brightness
    except Exception as e:
        print(f"Error reading brightness: {e}")
        return 0

def adjust_brightness(value):
    """
    Adjusts the screen brightness to the specified value and writes it to a file.

    Args:
        value (int): The new brightness value to set.

    Description:
        - Writes the new brightness value to the brightness file.
        - Prints a success message if the operation is successful.
        - If an error occurs (e.g., file I/O issues), it prints an error message.
    """

    global brightness
    brightness = value
    try:
        with open(brightness_file, "w") as file:
            file.write(str(value))
        print(f"Brightness adjusted to {value}")
        
    except Exception as e:
        print(f"Error adjusting brightness: {e}")

def decrease_brightness():
    """
    Decreases the screen brightness by 15 units, ensuring it does not go below 0.

    Returns:
        int: The new brightness value if successful, or 0 if an error occurs.

    Description:
        - Reads the current brightness value from the file.
        - Decreases the brightness by 15 units, ensuring it does not go below 0.
        - Updates the brightness file with the new value using `adjust_brightness`.
    """

    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        new_brightness = max(current_brightness - 15, 0)  # Ensure brightness doesn't go below 10
        adjust_brightness(new_brightness)
        return new_brightness
    except Exception as e:
        print(f"Error decreasing brightness: {e}")
        return 0

def increase_brightness():
    """
    Increases the screen brightness by 15 units, ensuring it does not exceed 255.

    Returns:
        int: The new brightness value if successful, or 0 if an error occurs.

    Description:
        - Reads the current brightness value from the file.
        - Increases the brightness by 15 units, ensuring it does not exceed 255.
        - Updates the brightness file with the new value using `adjust_brightness`.
    """

    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        new_brightness = min(current_brightness + 15, 255)  # Adjust 20 to your desired increment
        adjust_brightness(new_brightness)
        return new_brightness
    except Exception as e:
        print(f"Error increasing brightness: {e}")
        return 0

def save_rpm(rpm_max, shift):
    """
    Saves the maximum RPM and shift RPM values to a file.

    Args:
        rpm_max (int): The maximum RPM value.
        shift (int): The shift RPM value.

    Description:
        - Writes the maximum RPM and shift RPM values to the "Data/RPM.txt" file, separated by a comma.
    """

    with open("Data/RPM.txt", "w") as file:
        file.write(f"{rpm_max},{shift}")

def load_rpm():
    """
    Loads the maximum RPM and shift RPM values from a file.

    Returns:
        tuple: A tuple containing the maximum RPM value and the shift RPM value.

    Description:
        - Reads the RPM and shift values from the "Data/RPM.txt" file.
        - If the file does not exist or an error occurs, it returns default values of 8000 for max RPM and 6500 for shift RPM.
    """

    try:
        with open("Data/RPM.txt", "r") as file:
            data = file.read().split(",")
            rpm_max = int(data[0])
            shift = int(data[1])
    except Exception as e:
        print(e)
        rpm_max = 8000
        shift = 6500

    return rpm_max, shift

def check_wifi():
    """
    Checks the Wi-Fi status from the wifi.txt file.

    Returns:
        int: The Wi-Fi status (1 if connected, 0 if not).

    Description:
        - Reads the Wi-Fi status from the "Data/wifi.txt" file.
        - If an error occurs (e.g., file not found), it defaults to returning 0 (not connected).
    """

    try:
        with open("Data/wifi.txt", "r") as file:
            wifi = int(file.readline())
    except Exception:
        wifi = 0
    return wifi

def draw_text(screen, text, font, color, x, y, max_width=None):
    """
    Draws text on the screen with word wrapping support.

    Args:
        screen (pygame.Surface): The surface to draw the text on.
        text (str): The text to be displayed.
        font (pygame.font.Font): The font used for the text.
        color (tuple): The color of the text in (R, G, B) format.
        x (int): The x-coordinate of the text's starting position.
        y (int): The y-coordinate of the text's starting position.
        max_width (int, optional): The maximum width for the text before wrapping. Defaults to the screen width.

    Description:
        - Splits the text into words and calculates the space needed to render each line.
        - Wraps the text so it fits within the specified `max_width`.
        - Draws each line of text at the specified (x, y) position.
    """

    words = text.split(' ')
    space_width, _ = font.size(' ')
    max_width = max_width or SCREEN_WIDTH
    
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_width, _ = font.size(word)
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width + space_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width + space_width
    
    lines.append(' '.join(current_line))
    
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        text_rect = text_surface.get_rect(center=(x, y + i * font.get_height()))
        screen.blit(text_surface, text_rect)

def draw_rounded_rect(surface, color, rect, radius):
    """
    Draws a rectangle with rounded corners on the specified surface.

    Args:
        surface (pygame.Surface): The surface to draw the rounded rectangle on.
        color (tuple): The color of the rectangle in (R, G, B) format.
        rect (tuple): The rectangle's position and size in the form (x, y, width, height).
        radius (int): The radius of the rounded corners.

    Description:
        - Draws a rectangle with rounded corners using arcs and circles for the corners.
        - The rectangle's sides are drawn separately to avoid overlapping the corners.
    """

    # Draw the rounded corners using arcs
    x, y, width, height = rect
    pygame.draw.rect(surface, color, pygame.Rect(x + radius, y, width - 2 * radius, height))
    pygame.draw.rect(surface, color, pygame.Rect(x, y + radius, width, height - 2 * radius))
    
    pygame.draw.arc(surface, color, pygame.Rect(x, y, 2 * radius, 2 * radius), pi, 1.5 * pi, 0)
    pygame.draw.arc(surface, color, pygame.Rect(x + width - 2 * radius, y, 2 * radius, 2 * radius), 1.5 * pi, 2 * pi, 0)
    pygame.draw.arc(surface, color, pygame.Rect(x, y + height - 2 * radius, 2 * radius, 2 * radius), 0, 0.5 * pi, 0)
    pygame.draw.arc(surface, color, pygame.Rect(x + width - 2 * radius, y + height - 2 * radius, 2 * radius, 2 * radius), 0.5 * pi, pi, 0)

    # Fill the corners with the color
    corners = [(x + radius, y + radius),
               (x + width - radius, y + radius),
               (x + width - radius, y + height - radius),
               (x + radius, y + height - radius)]
    for corner in corners:
        pygame.draw.circle(surface, color, corner, radius)

def display_logo(screen):
    """
    Displays the Chevrolet logo with a rotating and scaling animation on the given screen.
    
    Args:
        screen (pygame.Surface): The pygame surface where the logo will be displayed.
    
    Description:
        - The logo is rotated and scaled continuously during a 3-second animation.
        - The animation ends after the specified duration.
        - The screen is filled with black color during each frame of the animation.
        - A text "Developed by Carson Spaniel" is displayed at the bottom of the screen.
    """

    logo = pygame.image.load("Images/chevy.jpg").convert_alpha()
    logo_rect = logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Animation variables
    rotation_angle = 0
    scale = 0.6
    animation_duration = 3
    start_time = time.time()

    while time.time() - start_time < animation_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(BLACK)

        # Rotate and scale the logo
        rotated_logo = pygame.transform.rotozoom(logo, rotation_angle, scale)
        rotated_rect = rotated_logo.get_rect(center=logo_rect.center)
        screen.blit(rotated_logo, rotated_rect)

        draw_text(screen, "Developed by Carson Spaniel", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

        pygame.display.flip()

        scale += 0.003

        pygame.time.Clock().tick(FPS)
    
def calculate_mpg(speed, maf):
    """
    Calculates the fuel efficiency in miles per gallon (MPG).

    Args:
        speed (float): The speed of the vehicle in miles per hour.
        maf (float): The mass air flow in grams per second.

    Returns:
        float: The calculated MPG value, or 0 if speed or MAF is zero.

    Description:
        - Converts MAF from grams per second to grams per hour.
        - Converts grams per hour to pounds per hour.
        - Converts pounds per hour to gallons per hour.
        - Calculates and returns the MPG based on the speed and gallons per hour.
    """

    if speed == 0 or maf == 0:
        return 0
    
    maf_gph = maf * 3600  # Convert MAF to grams per hour
    maf_pph = maf_gph / 453.592  # Convert grams per hour to pounds per hour
    gph = maf_pph / 6.17  # Convert pounds per hour to gallons per hour

    mpg = speed / gph
    return round(mpg * 10, 1)

def load_supported():
    """
    Loads supported PIDs from a file.

    Returns:
        list: A list of supported PIDs.

    Description:
        - Reads the "Data/supported.txt" file and loads each line as a PID.
        - If an error occurs while loading, it prints an error message and returns an empty list.
    """

    supported = []
    try:
        with open("Data/supported.txt", 'r') as file:
            supported = file.read().splitlines()  # Load each PID as a list item
    except Exception as e:
        print(f"Error loading supported PIDs from file: {e}")
    return supported

def save_supported(supported):
    """
    Saves supported PIDs to a file.

    Args:
        supported (list): A list of supported PIDs.

    Description:
        - Writes each PID in the list to the "Data/supported.txt" file.
        - If an error occurs during the save operation, it prints an error message.
    """

    try:
        with open("Data/supported.txt", 'w') as file:
            for pid in supported:
                file.write(f"{pid}\n")
    except Exception as e:
        print(f"Error saving supported PIDs to file: {e}")

def tint_image(image, tint_color):
    """
    Applies a tint to an image.

    Args:
        image (pygame.Surface): The original image to be tinted.
        tint_color (tuple): The color used for tinting in (R, G, B) format.

    Returns:
        pygame.Surface: A new tinted image.

    Description:
        - Creates a copy of the original image to avoid modifying it.
        - Applies the tint using the specified color and returns the tinted image.
    """

    tinted_image = image.copy()
    tinted_image.fill(tint_color, special_flags=pygame.BLEND_RGB_MULT)
    return tinted_image

def find_images(directory):
    """
    Finds and returns a list of image files in the specified directory.

    Args:
        directory (str): The directory to search for image files.

    Returns:
        list: A sorted list of relative paths to the found image files.

    Description:
        - Searches the specified directory and its subdirectories for image files
          with specified extensions (e.g., .jpg, .png).
        - Returns a sorted list of the found image file paths.
    """

    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
    image_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                relative_path = os.path.relpath(os.path.join(root, file))
                image_files.append(relative_path)

    image_files.sort()
    return image_files

def read_info(pages, len_images):
    """
    Reads and loads user settings from a data file.

    Args:
        pages (list): A list of pages for navigation.
        len_images (int): The total number of images.

    Returns:
        tuple: A tuple containing various settings including the current page and other preferences.

    Description:
        - Reads the current page and various user settings from "Data/info.txt".
        - If an error occurs, it returns default settings.
    """

    try:
        with open("Data/info.txt", "r") as file:
            current_page_x = int(file.readline())
            if current_page_x < 0 or current_page_x >= len(pages):
                current_page_x = 0

            current_page_y = int(file.readline())
            if current_page_y < 0 or current_page_y >= len(pages[current_page_x]):
                current_page_y = 0

            current_page = (current_page_x, current_page_y)
            shift_light = int(file.readline())
            delay = int(file.readline())
            optimize = int(file.readline())
            font_index = int(file.readline())
            background_1_index = int(file.readline())
            background_2_index = int(file.readline())
            shift_color_1 = int(file.readline())
            shift_color_2 = int(file.readline())
            shift_color_3 = int(file.readline())
            shift_color_4 = int(file.readline())
            shift_padding = int(file.readline())
            image_index = int(file.readline())

    except Exception as e:
        print(e)
        current_page = (0, 0)
        shift_light = True
        delay = False
        optimize = False
        font_index = 46
        background_1_index = 23
        background_2_index = 45
        shift_color_1 = 12
        shift_color_2 = 8
        shift_color_3 = 0
        shift_color_4 = 31
        shift_padding = 100
        image_index = 0

    if image_index >= len_images:
        image_index = 0

    return (current_page, shift_light, delay, optimize, font_index, 
            background_1_index, background_2_index, 
            shift_color_1, shift_color_2, shift_color_3, 
            shift_color_4, shift_padding, image_index)

def write_info(current_page, shift_light, delay, optimize, font_index, background_1_index, background_2_index, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding, image_index):
    """
    Writes user settings to a data file.

    Args:
        current_page (tuple): The current page index as (x, y).
        shift_light (bool): The shift light setting.
        delay (bool): The delay setting.
        optimize (bool): The optimize setting.
        font_index (int): The index of the selected font.
        background_1_index (int): The index of the first background.
        background_2_index (int): The index of the second background.
        shift_color_1 (int): The first shift color index.
        shift_color_2 (int): The second shift color index.
        shift_color_3 (int): The third shift color index.
        shift_color_4 (int): The fourth shift color index.
        shift_padding (int): The padding for shifts.
        image_index (int): The selected image index.

    Description:
        - Writes the provided settings to "Data/info.txt".
    """
    
    with open("Data/info.txt", "w") as file:
        file.write(str(current_page[0]))
        file.write(f'\n{str(current_page[1])}')
        file.write(f'\n{str(int(shift_light))}')
        file.write(f'\n{str(int(delay))}')
        file.write(f'\n{str(int(optimize))}')
        file.write(f'\n{str(int(font_index))}')
        file.write(f'\n{str(int(background_1_index))}')
        file.write(f'\n{str(int(background_2_index))}')
        file.write(f'\n{str(int(shift_color_1))}')
        file.write(f'\n{str(int(shift_color_2))}')
        file.write(f'\n{str(int(shift_color_3))}')
        file.write(f'\n{str(int(shift_color_4))}')
        file.write(f'\n{str(int(shift_padding))}')
        file.write(f'\n{str(int(image_index))}')