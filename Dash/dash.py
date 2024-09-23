import random
import threading
from Helper.brain import *
from Helper.pages import *
from Helper.events import *

# Load Brightness
brightness = get_brightness()

# Load RPM
rpm_max,shift = load_rpm()

# Environment Variables
DEV = False
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
experimental = False
query_times = {
        'rpm': 0, 'speed': 0, 'fuel_level': 0, 
        'voltage': 0, 'air_temp': 0, 'codes': 0
    }

pages = [
    ["Main"],
    ["Custom", "Color1"],
    ["Trouble"],
    ["Settings", "RPM","Info"],
    # ["Off"]
]

# Function to constantly try to connect
def connect_thread():
    try_connect(DEV)
    while not connect:
        time.sleep(5)
        try_connect(DEV)
    
    # Run Queries on Separate Thread
    threading.Thread(target=query, daemon=True).start()

# Function for calculating the execution time of queries
def measure_time(query_func, *args):
    start_time = time.time()
    result = query_func(*args)
    end_time = time.time()
    exec_time = end_time - start_time
    return result, exec_time

# Function for calculating a rolling average
def rolling_avg(old_avg, new_value, count):
    return (old_avg * (count - 1) + new_value) / count

# Function for making the queries for everything needed in the dash
def query():
    # Get global variables
    global clear, cleared, rpm, speed, maf, mpg, fuel_level, voltage, air_temp, codes, experimental, query_times

    delay1 = time.time()
    delay2 = time.time()

    # Initial delay times are placeholders; they will adapt dynamically
    first_delay = 1.0
    second_delay = 1.0
    
    # Track how many times each query is executed to calculate rolling average
    execution_counts = {key: 1 for key in query_times}

    # Made it these specific times so that all queries only line up every 9.1 seconds
    first_delay = .7
    second_delay = 1.3
    while logging and connect:
        if not experimental:
            first_delay = .7
            second_delay = 1.3
            current_time = time.time()
            try:
                if pages[current_page[0]][current_page[1]] == "Main":
                    # Get RPM
                    if '0x0C' in supported:
                        response_rpm = connection.query(obd.commands.RPM)
                        if not response_rpm.is_null():
                            rpm = int(round(response_rpm.value.magnitude,0))
                    
                    # Run every first_delay seconds or if delay is on
                    if current_time - delay1 >= first_delay or delay:
                        delay1 = current_time

                        if not optimize:
                            # Get Speed and MPG
                            if '0x0D' in supported and '0x10' in supported:
                                response_speed = connection.query(obd.commands.SPEED)  # Vehicle speed
                                response_maf = connection.query(obd.commands.MAF)      # Mass Air Flow
                                if not response_speed.is_null() and not response_maf.is_null():
                                    speed = response_speed.value.to('mile/hour').magnitude
                                    maf = response_maf.value.to('gram/second').magnitude
                                    mpg = calculate_mpg(speed, maf)

                        # Get fuel level
                        if '0x2F' in supported:
                            response_fuel_level = connection.query(obd.commands.FUEL_LEVEL)
                            if not response_fuel_level.is_null():
                                fuel_level = response_fuel_level.value.magnitude

                    # Run every second_delay second or if delay is on
                    if not optimize:
                        if current_time - delay2 >= second_delay or delay:
                            delay2 = current_time

                            # Get voltage
                            if '0x42' in supported:
                                response_voltage = connection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
                                if not response_voltage.is_null():
                                    voltage = response_voltage.value.magnitude
                            
                            # Get air temperature
                            if '0x46' in supported:
                                response_air_temp = connection.query(obd.commands.AMBIANT_AIR_TEMP)
                                if not response_air_temp.is_null():
                                    air_temp = response_air_temp.value.magnitude

                            # Get CEL codes
                            response_cel = connection.query(obd.commands.GET_DTC)
                            if not response_cel.is_null():
                                codes = response_cel.value

                elif pages[current_page[0]][current_page[1]] == "Trouble" or pages[current_page[0]][current_page[1]] == "RPM":
                    # Get RPM
                    if '0x0C' in supported:
                        response_rpm = connection.query(obd.commands.RPM)
                        if not response_rpm.is_null():
                            rpm = int(round(response_rpm.value.magnitude,0))

                        # Attempt to clear CEL
                        if clear:
                            if rpm == 0: # Only run if engine is off

                                response_clear = connection.query(obd.commands.CLEAR_DTC)

                                if not response_clear.is_null():
                                    cleared = 1 # Success
                                    clear = False
                                else:
                                    cleared = 2 # Error
                            else:
                                cleared = 3 # Engine needs to be off

                time.sleep(.03) # Increasing this will slow down queries

            except Exception as e:
                print(f'An error occured: {e}')
                print('Restarting script')
                exit()
        else:
            current_time = time.time()
            try:
                # Query only if "Main" page is active
                if pages[current_page[0]][current_page[1]] == "Main":
                    # Get RPM
                    if '0x0C' in supported:
                        response_rpm, rpm_time = measure_time(connection.query, obd.commands.RPM)
                        query_times['rpm'] = rolling_avg(query_times['rpm'], rpm_time, execution_counts['rpm'])
                        execution_counts['rpm'] += 1
                        if not response_rpm.is_null():
                            rpm = int(round(response_rpm.value.magnitude, 0))

                    # Handle the first batch of queries (speed, MPG, fuel level)
                    if current_time - delay1 >= first_delay:
                        delay1 = current_time

                        # Get Speed and MPG
                        if '0x0D' in supported and '0x10' in supported:
                            response_speed, speed_time = measure_time(connection.query, obd.commands.SPEED)
                            response_maf, maf_time = measure_time(connection.query, obd.commands.MAF)
                            query_times['speed'] = rolling_avg(query_times['speed'], speed_time + maf_time, execution_counts['speed'])
                            execution_counts['speed'] += 1
                            
                            if not response_speed.is_null() and not response_maf.is_null():
                                speed = response_speed.value.to('mile/hour').magnitude
                                maf = response_maf.value.to('gram/second').magnitude
                                mpg = calculate_mpg(speed, maf)

                        # Get fuel level
                        if '0x2F' in supported:
                            response_fuel_level, fuel_time = measure_time(connection.query, obd.commands.FUEL_LEVEL)
                            query_times['fuel_level'] = rolling_avg(query_times['fuel_level'], fuel_time, execution_counts['fuel_level'])
                            execution_counts['fuel_level'] += 1
                            if not response_fuel_level.is_null():
                                fuel_level = response_fuel_level.value.magnitude

                    # Handle the second batch of queries (voltage, air temperature, CEL codes)
                    if current_time - delay2 >= second_delay:
                        delay2 = current_time

                        # Get voltage
                        if '0x42' in supported:
                            response_voltage, voltage_time = measure_time(connection.query, obd.commands.CONTROL_MODULE_VOLTAGE)
                            query_times['voltage'] = rolling_avg(query_times['voltage'], voltage_time, execution_counts['voltage'])
                            execution_counts['voltage'] += 1
                            if not response_voltage.is_null():
                                voltage = response_voltage.value.magnitude

                        # Get air temperature
                        if '0x46' in supported:
                            response_air_temp, air_temp_time = measure_time(connection.query, obd.commands.AMBIANT_AIR_TEMP)
                            query_times['air_temp'] = rolling_avg(query_times['air_temp'], air_temp_time, execution_counts['air_temp'])
                            execution_counts['air_temp'] += 1
                            if not response_air_temp.is_null():
                                air_temp = response_air_temp.value.magnitude

                        # Get CEL codes
                        response_cel, codes_time = measure_time(connection.query, obd.commands.GET_DTC)
                        query_times['codes'] = rolling_avg(query_times['codes'], codes_time, execution_counts['codes'])
                        execution_counts['codes'] += 1
                        if not response_cel.is_null():
                            codes = response_cel.value

                # Calculate the average time taken by the queries
                avg_time_first_batch = query_times['speed'] + query_times['fuel_level']
                avg_time_second_batch = query_times['voltage'] + query_times['air_temp'] + query_times['codes']

                # Dynamically calculate delays based on the average query time, with a small buffer
                first_delay = avg_time_first_batch * 1.2  # 20% buffer
                second_delay = avg_time_second_batch * 1.2  # 20% buffer

                # Ensure minimum delay values to prevent over-querying
                first_delay = max(first_delay, 0.5)
                second_delay = max(second_delay, 0.5)

                # Short sleep to avoid overloading the CPU
                time.sleep(0.03)

            except Exception as e:
                print(f'An error occurred: {e}')
                print('Restarting script')
                exit()

# Main function for the Pygame interface
def main():
    # Get global variables
    global delay, optimize, brightness, rpm_max, shift, cleared, clear, rpm, speed, maf, mpg, fuel_level, voltage, air_temp, codes, logging, exit_text, current_page, experimental

    # Initialize variables
    FLIP = False
    mouse_button_down = False
    skip = True
    changed_image = False
    previous_info = []

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
                        show_fps, experimental = development_event(mouseX, mouseY, show_fps, experimental)

                    elif pages[current_page[0]][current_page[1]] == "Custom":
                        font_index, background_1_index, background_2_index, image_index, changed_image = custom_event(mouseX, mouseY, images, font_index, background_1_index, background_2_index, image_index, changed_image)
                    
                    elif pages[current_page[0]][current_page[1]] == "Color1":
                        shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding = color_1_event(mouseX, mouseY, shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding)

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

        if DEV:
            # Set random variables for testing purposes
            rpm = random.randint(max(0,rpm-50), min(rpm+60,rpm_max))
            speed = random.uniform(max(0,speed-10), min(speed+100,80))* 0.621371
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
                developmental_page(screen, FONT_COLOR, show_fps, experimental, query_times)
            
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
