import random
import obd
import threading
import math
from Helper.brain import *
from Helper.pages import *
from Helper.events import *

from collections import defaultdict

# Load Brightness
brightness = get_brightness()

# Load RPM
rpm_max, shift = load_rpm()

# Load Performance Stats
top_speed = load_performance()

# Environment Variables
DEV = True
PI = False
SYSTEM_VERSION = "2.7.0"

# Global Variables
supported = []
connect = False
delay = 0
optimize = 0
cleared = 0
clear = False
rpm = 0
speed = 0
maf = 0
mpg = 0
fuel_level= 0
voltage = 0
air_temp = 0
codes = []
logging = True
exit_text = "Exiting..."
connection = None
current_page = (0, 0)
development_mode = False

# Initialize a dictionary to store only the rolling averages
query_times = defaultdict(lambda: {"average": None})

pages = [
    ["Main"],
    ["Performance"],
    ["Custom", "Color1"],
    ["Trouble"],
    ["Settings", "RPM","Info"],
    # ["Off"]
]

def try_connect():
    """
    Attempts to establish a connection to the OBD-II adapter via Bluetooth, unless development mode is enabled.

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

# Function to constantly try to connect
def connect_thread():
    try_connect()
    while not connect:
        time.sleep(5)
        try_connect()
    
    # Run Queries on Separate Thread
    threading.Thread(target=query, daemon=True).start()

# Function to update the rolling average using the exponential moving average (EMA)
def update_rolling_average(query_name, time_taken, alpha=0.1):
    if query_times[query_name]["average"] is None:
        # If no previous average, set the first one
        query_times[query_name]["average"] = time_taken
    else:
        # Update the rolling average using the exponential moving average formula
        avg = query_times[query_name]["average"]
        query_times[query_name]["average"] = alpha * time_taken + (1 - alpha) * avg

# Function for making the queries for everything needed in the dash
def query():
    # Get global variables
    global clear, cleared, rpm, speed, maf, mpg, fuel_level, voltage, air_temp, codes, development_mode

    delay1 = time.time()
    delay2 = time.time()

    # Made it these specific times so that all queries only line up every 9.1 seconds
    first_delay = .7
    second_delay = 1.3
    while logging and connect:
        current_time = time.time()
        try:
            if pages[current_page[0]][current_page[1]] == "Main":
                # Get RPM
                if '0x0C' in supported:
                    if development_mode:
                        start_time = time.time()  # Track start time
                    response_rpm = connection.query(obd.commands.RPM)
                    if not response_rpm.is_null():
                        rpm = int(round(response_rpm.value.magnitude, 0))
                    if development_mode:
                        query_time = time.time() - start_time  # Calculate query time
                        update_rolling_average("RPM", query_time)

                # Run every first_delay seconds or if delay is on
                if current_time - delay1 >= first_delay or delay:
                    delay1 = current_time

                    if not optimize:
                        # Get Speed and MPG
                        if '0x0D' in supported and '0x10' in supported:
                            if development_mode:
                                start_time_speed = time.time()  # Start timer for speed query
                            response_speed = connection.query(obd.commands.SPEED)  # Vehicle speed
                            if not response_speed.is_null():
                                speed = response_speed.value.to('mile/hour').magnitude
                            if development_mode:
                                query_time_speed = time.time() - start_time_speed  # Time taken for speed query
                                update_rolling_average("Speed", query_time_speed)  # Update rolling average for speed

                            if development_mode:
                                start_time_maf = time.time()  # Start timer for MAF query
                            response_maf = connection.query(obd.commands.MAF)  # Mass Air Flow
                            if not response_maf.is_null():
                                maf = response_maf.value.to('gram/second').magnitude
                            if development_mode:
                                query_time_maf = time.time() - start_time_maf  # Time taken for MAF query
                                update_rolling_average("MAF", query_time_maf)  # Update rolling average for MAF

                            # If both speed and MAF are valid, calculate MPG
                            if not response_speed.is_null() and not response_maf.is_null():
                                mpg = calculate_mpg(speed, maf)

                    # Get fuel level
                    if '0x2F' in supported:
                        if development_mode:
                            start_time = time.time()
                        response_fuel_level = connection.query(obd.commands.FUEL_LEVEL)
                        if not response_fuel_level.is_null():
                            fuel_level = response_fuel_level.value.magnitude
                        if development_mode:
                            query_time = time.time() - start_time
                            update_rolling_average("Fuel_Level", query_time)

                # Run every second_delay second or if delay is on
                if not optimize:
                    if current_time - delay2 >= second_delay or delay:
                        delay2 = current_time

                        # Get voltage
                        if '0x42' in supported:
                            if development_mode:
                                start_time = time.time()
                            response_voltage = connection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
                            if not response_voltage.is_null():
                                voltage = response_voltage.value.magnitude
                            if development_mode:
                                query_time = time.time() - start_time
                                update_rolling_average("Voltage", query_time)

                        # Get air temperature
                        if '0x46' in supported:
                            if development_mode:
                                start_time = time.time()
                            response_air_temp = connection.query(obd.commands.AMBIANT_AIR_TEMP)
                            if not response_air_temp.is_null():
                                air_temp = response_air_temp.value.magnitude
                            if development_mode:
                                query_time = time.time() - start_time
                                update_rolling_average("Air_Temp", query_time)

            elif pages[current_page[0]][current_page[1]] == "Trouble" or pages[current_page[0]][current_page[1]] == "RPM":
                # Get RPM
                if '0x0C' in supported:
                    if development_mode:
                        start_time = time.time()
                    response_rpm = connection.query(obd.commands.RPM)
                    if not response_rpm.is_null():
                        rpm = int(round(response_rpm.value.magnitude, 0))
                    if development_mode:
                        query_time = time.time() - start_time
                        update_rolling_average("RPM_Trouble", query_time)

                    # Get CEL codes
                    if development_mode:
                        start_time = time.time()
                    response_cel = connection.query(obd.commands.GET_DTC)
                    if not response_cel.is_null():
                        codes = response_cel.value
                    if development_mode:
                        query_time = time.time() - start_time
                        update_rolling_average("CEL_Codes", query_time)

                    # Attempt to clear CEL
                    if clear:
                        if rpm == 0:  # Only run if engine is off
                            if development_mode:
                                start_time = time.time()
                            response_clear = connection.query(obd.commands.CLEAR_DTC)
                            if not response_clear.is_null():
                                cleared = 1  # Success
                                clear = False
                            else:
                                cleared = 2  # Error
                            if development_mode:
                                query_time = time.time() - start_time
                                update_rolling_average("Clear_DTC", query_time)
                        else:
                            cleared = 3  # Engine needs to be off
    
            elif pages[current_page[0]][current_page[1]] == "Performance":
                if '0x0C' in supported:
                    if development_mode:
                        start_time = time.time()  # Track start time
                    response_rpm = connection.query(obd.commands.RPM)
                    if not response_rpm.is_null():
                        rpm = int(round(response_rpm.value.magnitude, 0))
                    if development_mode:
                        query_time = time.time() - start_time  # Calculate query time
                        update_rolling_average("RPM_Performance", query_time)

                # Get Speed
                if '0x0D' in supported:
                    if development_mode:
                        start_time_speed = time.time()  # Start timer for speed query
                    response_speed = connection.query(obd.commands.SPEED)  # Vehicle speed
                    if not response_speed.is_null():
                        speed = response_speed.value.to('mile/hour').magnitude
                    if development_mode:
                        query_time_speed = time.time() - start_time_speed  # Time taken for speed query
                        update_rolling_average("Speed_Performance", query_time_speed)  # Update rolling average for speed

            time.sleep(.03)  # Increasing this will slow down queries

        except Exception as e:
            print(f'An error occurred: {e}')
            print('Restarting script')
            exit()
            
# Main function for the Pygame interface
def main():
    # Get global variables
    global delay, optimize, brightness, rpm_max, shift, cleared, clear, rpm, speed, maf, mpg, fuel_level, voltage, air_temp, codes, logging, exit_text, current_page, development_mode, top_speed

    # Initialize variables
    FLIP = False
    mouse_button_down = False
    skip = True
    changed_image = False
    previous_info = []
    last_top_speed = 0
    tracking = False
    speed_times = []
    performance_graph_added = False
    elapsed_time = None

    # Show development things in DEV mode
    if DEV:
        development_mode = True
        show_fps = True
    else:
        development_mode = False
        show_fps = False

    swipe_start_x = 0
    swipe_start_y = 0
    swipe_threshold = 50  # Threshold for swipe detection (in pixels)

    # Find images
    images = find_images("Images/backgrounds/")

    # Load saved information
    current_page, shift_light, delay, optimize, font_index, background_1_index, background_2_index, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding, image_index = read_info(pages, len(images))

    # Load Pygame
    if not PI:
        screen_2 = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        screen_2 = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Smart Dash")
    clock = pygame.time.Clock()

    if DEV:
        # Set fake initial values
        rpm = 650
        fuel_level = random.randint(0,100)
        speed = 0
        maf = 6
        voltage = 15.5
        current_gear = 0
    else:
        # Keep trying to connect on Separate Thread
        threading.Thread(target=connect_thread, daemon=True).start()

        # Display Chevrolet logo
        display_logo(screen_2)

    # Load the image you want to display
    background_image = pygame.image.load(images[image_index])
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Development variables
    develop_added = False

    while logging:
        if development_mode:
            if not develop_added:
                pages.append(["Development"])
                develop_added = True
        elif develop_added:
            pages.remove(["Development"])
            develop_added = False

        if changed_image:
            # Load and change the new background
            background_image = pygame.image.load(images[image_index])
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            changed_image = False

        FONT_COLOR = COLORS[font_index] # Default font color
        BACKGROUND_1_COLOR = COLORS[background_1_index] # Default background 1 color
        BACKGROUND_2_COLOR = COLORS[background_2_index] # Default background 2 color

        # Create a mask surface that will use the BACKGROUND_2_COLOR and become transparent
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Set the color key to make BACKGROUND_2_COLOR transparent on the mask
        screen.set_colorkey(BACKGROUND_2_COLOR)

        # Tint the background image with BACKGROUND_2_COLOR
        tinted_background = tint_image(background_image, BACKGROUND_2_COLOR)

        # Check if connected to internet
        wifi = check_wifi()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_button_down: # If touch is in progress
                    current_page, mouse_button_down = swipe_event(mouse_button_down, event, swipe_start_x, swipe_start_y, swipe_threshold, current_page, pages)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_down = True
                swipe_start_x, swipe_start_y = event.pos  # Record the start position of the touch

                mouseX, mouseY = event.pos[0], event.pos[1]

                if FLIP:
                    mouseY = SCREEN_HEIGHT - mouseY

                if event.button == 1:  # Left mouse button

                    if pages[current_page[0]][current_page[1]] == "RPM":
                        rpm_max, shift = rpm_event(mouseX, mouseY, rpm_max, shift)

                    elif pages[current_page[0]][current_page[1]] == "Settings":
                        brightness, optimize, FLIP, delay = settings_event(mouseX, mouseY, brightness, optimize, FLIP, delay)

                    elif pages[current_page[0]][current_page[1]] == "Trouble":
                        clear = trouble_event(mouseX, mouseY, clear)

                    elif pages[current_page[0]][current_page[1]] == "Info":
                        logging, exit_text, development_mode = info_event(mouseX, mouseY, wifi, logging, exit_text, development_mode)
                    
                    elif pages[current_page[0]][current_page[1]] == "Development":
                        show_fps = development_event(mouseX, mouseY, show_fps)

                    elif pages[current_page[0]][current_page[1]] == "Custom":
                        font_index, background_1_index, background_2_index, image_index, changed_image = custom_event(mouseX, mouseY, images, font_index, background_1_index, background_2_index, image_index, changed_image)
                    
                    elif pages[current_page[0]][current_page[1]] == "Color1":
                        shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding = color_1_event(mouseX, mouseY, shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding)
                    
                    elif pages[current_page[0]][current_page[1]] == "Performance":
                        tracking = performance_event(mouseX, mouseY, tracking)

                skip = True
                time.sleep(.1) # How long someone presses for a single click
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_button_down = False

        # If holding down button
        if mouse_button_down:
            if not skip:
                mouseX, mouseY = pygame.mouse.get_pos()

                if pages[current_page[0]][current_page[1]] == "RPM":
                    rpm_max, shift = rpm_event(mouseX, mouseY, rpm_max, shift)

                elif pages[current_page[0]][current_page[1]] == "Settings":
                    brightness, optimize, FLIP, delay = settings_event(mouseX, mouseY, brightness, optimize, FLIP, delay, True)
                
                elif pages[current_page[0]][current_page[1]] == "Custom":
                    font_index, background_1_index, background_2_index, image_index, changed_image = custom_event(mouseX, mouseY, images, font_index, background_1_index, background_2_index, image_index, changed_image, True)

                elif pages[current_page[0]][current_page[1]] == "Color1":
                    shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding = color_1_event(mouseX, mouseY, shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding)

                time.sleep(.1) # How long it takes to cycle to the next item
            
            skip = False
        
        # Only write to file if the information has changed
        new_info = [current_page, shift_light, delay, optimize, font_index, background_1_index, background_2_index, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding, image_index]
        if new_info != previous_info:
            write_info(current_page, shift_light, delay, optimize, font_index, background_1_index, background_2_index, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding, image_index)
            previous_info = new_info

        top_speed, last_top_speed, speed_times, graph_made, elapsed_time, zero_to_sixty_time, zero_to_hundred_time, eighth_mile_time, quarter_mile_time = calculate_performance(FONT_COLOR, speed, top_speed, last_top_speed, tracking, speed_times, rpm, elapsed_time)

        if graph_made:
            if not performance_graph_added:
                pages[1].append("Speed_Time")
                pages[1].append("Speed_RPM")
                performance_graph_added = True

        if DEV:
            # Define maximum speed
            max_speed = 300

            # Define gear ratios for 6 gears
            gear_ratios = [3.80, 2.10, 1.50, 1.20, 1.00, 0.80]
            
            # Determine current gear ratio
            current_ratio = gear_ratios[current_gear]

            # RPM calculation with some randomness to simulate fluctuations
            rpm = random.randint(max(0, rpm - 10), min(rpm + 10, rpm_max))

            if tracking:
                # Check if RPM exceeds shift point, shift up if possible
                if rpm >= shift + random.randint(-5, 5) and current_gear < len(gear_ratios) - 1:
                    current_gear += 1
                    current_ratio = gear_ratios[current_gear]
                    # Adjust RPM for new gear, simulating the effect of shifting
                    rpm = int(rpm * (1 - (current_ratio/max(gear_ratios))))

                # Increment RPM logarithmically for smooth progression
                rpm_increment = 10 * (current_ratio**2)
                rpm = min(int(rpm + rpm_increment), rpm_max)  # Increment RPM with cap at max RPM
                
                if rpm < rpm_max:
                    speed_increment = (current_ratio / max(gear_ratios)) * .5

                    # Increase speed
                    speed += speed_increment

                    # Ensure speed does not exceed max_speed
                    speed = min(speed, max_speed)

            # Ensure RPM does not exceed rpm_max
            rpm = min(rpm, rpm_max)

            maf = round(maf,0)
            maf = random.randint(max(1,maf-1), min(maf+1,80))
            mpg = calculate_mpg(speed, maf)
            if fuel_level<=0:
                fuel_level=100
            fuel_level -= .1
            voltage = random.uniform(max(14,voltage-.1), min(voltage+.1,15))
            air_temp = random.randint(0,50)
            if clear:
                cleared = random.randint(1,3)
                clear = False

            if cleared != 1:
                codes = [("P0104", "Mass or Volume Air Flow Circuit Intermittent"),("B0123", "This is a very long message to simulate a long description hoping for it to be cut off properly to have a consistent message flow."),("C0123", f"{' '.join(['*' for i in range(60)])}"), ("D0123", ""), ("E0123", "")]
            else:
                codes = []

        # Render pages
        try:
            if pages[current_page[0]][current_page[1]] == "Main":
                main_page(screen, FONT_COLOR, BACKGROUND_1_COLOR, BACKGROUND_2_COLOR, fuel_level, rpm, rpm_max, shift, optimize, shift_light, mpg, speed, air_temp, voltage, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding)
            
            elif pages[current_page[0]][current_page[1]] == "RPM":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                rpm_page(screen, FONT_COLOR, DEV, supported, rpm, rpm_max, shift, connect)

            elif pages[current_page[0]][current_page[1]] == "Settings":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                settings_page(screen, FONT_COLOR, brightness, optimize, delay)
            
            elif pages[current_page[0]][current_page[1]] == "Trouble":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                trouble_page(screen, FONT_COLOR, codes, cleared)
            
            elif pages[current_page[0]][current_page[1]] == "Info":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                info_page(screen, FONT_COLOR, SYSTEM_VERSION, wifi, development_mode)
            
            elif pages[current_page[0]][current_page[1]] == "Custom":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                custom_page(screen, FONT_COLOR, font_index, background_1_index, background_2_index, images, image_index)
            
            elif pages[current_page[0]][current_page[1]] == "Color1":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                color_1_page(screen, FONT_COLOR, shift, shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding)
            
            elif pages[current_page[0]][current_page[1]] == "Development":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                developmental_page(screen, FONT_COLOR, show_fps, query_times)

            elif pages[current_page[0]][current_page[1]] == "Performance":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                performance_page(screen, FONT_COLOR, BACKGROUND_2_COLOR, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding, rpm, shift, top_speed, last_top_speed, tracking, elapsed_time, zero_to_sixty_time, zero_to_hundred_time, eighth_mile_time, quarter_mile_time)            
            
            elif pages[current_page[0]][current_page[1]] == "Speed_Time":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                speed_time_graph_page(screen)

            elif pages[current_page[0]][current_page[1]] == "Speed_RPM":
                page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page)
                speed_rpm_graph_page(screen)       

            elif pages[current_page[0]][current_page[1]] == "Off":
                screen.fill(BLACK)
                
        except IndexError:
            current_page = (current_page[0],0)

        # Show FPS
        if development_mode and show_fps:
            draw_text(screen, f"{clock.get_fps():.1f}", font_small_clean, FONT_COLOR, SCREEN_WIDTH*.96, SCREEN_HEIGHT*.96)

        # Blit the tinted background image onto the screen first
        screen_2.blit(tinted_background, (0, 0))

        # Then blit the mask surface onto the screen (with transparency)
        screen_2.blit(screen, (0, 0))

        if FLIP:
            flipped_screen = pygame.transform.flip(screen_2, False, True)
            screen_2.blit(flipped_screen, (0, 0))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

    print(exit_text)

    if connect:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()
