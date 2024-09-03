import pygame
import obd
import time
import random
import math
import subprocess
import threading
from Helper.brain import *

# Load Brightness
BRIGHTNESS = get_brightness()

# Load RPM
RPM_MAX,SHIFT = load_rpm()

# Environment Variables
DEV = False
PI = True
SYSTEM_VERSION = "2.2.0"

# Global Variables
DELAY = 0
OPTIMIZE = 0
CLEARED = 0
CLEAR = False
rpm = 0
speed = 0
maf = 0
mpg = 0
fuel_level= 0
voltage = 0
air_temp = 0
codes = []
logging = True
internal_clock = 0
exit_text = "Exiting..."

# Attempt to connect to OBD-II Adapter
if not DEV:
    connect = False
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
                connect = True
                break
            else:
                print("Could not connect to OBD-II adapter.")
        except Exception:
            print('An error occurred.')
    if not connect:
        print('Exiting...')
        exit()

def query():
    # Get global variables
    global CLEAR, CLEARED, rpm, speed, maf, mpg, fuel_level, voltage, air_temp, codes

    delay1 = time.time()
    delay2 = time.time()

    # Made it these specific times so that all queries only line up every 9.1 seconds
    first_delay = .7
    second_delay = 1.3
    while logging:
        current_time = time.time()
        try:
            response_rpm = connection.query(obd.commands.RPM)

            # Setting the values
            if not response_rpm.is_null():
                rpm = int(round(response_rpm.value.magnitude,0))
            
            # Run every first_delay seconds or if DELAY is on
            if current_time - delay1 >= first_delay or DELAY:
                delay1 = current_time

                if not OPTIMIZE:
                    response_speed = connection.query(obd.commands.SPEED)  # Vehicle speed
                    response_maf = connection.query(obd.commands.MAF)      # Mass Air Flow

                    if not response_speed.is_null() and not response_maf.is_null():
                        speed = response_speed.value.to('mile/hour').magnitude
                        maf = response_maf.value.to('gram/second').magnitude
                        mpg = calculate_mpg(speed, maf)

                response_fuel_level = connection.query(obd.commands.FUEL_LEVEL)

                if not response_fuel_level.is_null():
                    fuel_level = response_fuel_level.value.magnitude

            # Run every second_delay second or if DELAY is on
            if not OPTIMIZE:
                if current_time - delay2 >= second_delay or DELAY:
                    delay2 = current_time

                    response_voltage = connection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
                    response_air_temp = connection.query(obd.commands.AMBIANT_AIR_TEMP)

                    if not response_voltage.is_null():
                        voltage = response_voltage.value.magnitude

                    if not response_air_temp.is_null():
                        air_temp = response_air_temp.value.magnitude

                    # Gather CEL codes
                    response_cel = connection.query(obd.commands.GET_DTC)
                    if not response_cel.is_null():
                        codes = response_cel.value

            # Attempt to clear CEL
            if CLEAR:
                if response_rpm.value.magnitude == 0: # Only run if engine is off

                    response_clear = connection.query(obd.commands.CLEAR_DTC)

                    if not response_clear.is_null():
                        CLEARED = 1 # Success
                        CLEAR = False
                    else:
                        CLEARED = 2 # Error
                else:
                    CLEARED = 3 # Engine needs to be off

            time.sleep(.1) # Increasing this will slow down queries

        except Exception as e:
            print(f'An error occured: {e}')
            print('Restarting script')
            exit()

# Main function for the Pygame interface
def main():
    # Get global variables
    global DELAY, OPTIMIZE, BRIGHTNESS, RPM_MAX, SHIFT, CLEARED, CLEAR, rpm, speed, maf, mpg, fuel_level, voltage, air_temp, codes, logging, internal_clock, exit_text

    # Initialize variables
    #pages = ["Main" , "Settings", "RPM", "Trouble"] #"Off"
    pages = [
        ["Main"],
        ["Settings", "RPM", "Custom","Info"],
        ["Trouble"]
    ]
    current_page = (0, 0)
    FLIP = False
    SHIFT_LIGHT = True
    mouse_button_down = False
    skip = True

    swipe_start_x = 0
    swipe_start_y = 0
    swipe_threshold = 50  # Threshold for swipe detection (in pixels)
    is_swiping = False

    # Load the last visited page
    try:
        with open("Data/info.txt", "r") as file:
            current_page_x = int(file.readline())
            if current_page_x < 0 or current_page_x >= len(pages):
                current_page_x = 0

            current_page_y = int(file.readline())
            if current_page_y < 0 or current_page_y >= len(pages[current_page_x]):
                current_page_y = 0

            current_page = (current_page_x, current_page_y)

            SHIFT_LIGHT = int(file.readline())
            DELAY = int(file.readline())
            OPTIMIZE = int(file.readline())
    except Exception:
        current_page = (0, 0)
        SHIFT_LIGHT = True
        DELAY = False
        OPTIMIZE = False

    # Load Pygame
    if not PI:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption("Smart Dash")
    clock = pygame.time.Clock()

    # Load images
    curve = pygame.image.load("Images/round2.png").convert_alpha()
    curveOut = pygame.transform.scale(curve, (curve.get_width() * 1.8, curve.get_height() * 1.6))
    curveIn = pygame.transform.scale(curve, (curve.get_width() * 1.4, curve.get_height() * 1.1))

    if DEV:
        # Set fake initial values
        rpm = 650
        fuel_level = random.randint(0,100)
        speed = 0
        maf = 6
        voltage = 15.5
    else:
        # Display Chevrolet logo
        display_logo(screen)

        # Run Queries on Separate Thread
        threading.Thread(target=query, daemon=True).start()

    while logging:
        try:
            with open("Data/wifi.txt", "r") as file:
                wifi = int(file.readline())
        except Exception:
            print("No wifi file.")
            wifi = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging = False

            elif event.type == pygame.MOUSEMOTION:
                if mouse_button_down:  # If touch is in progress
                    current_x, current_y = event.pos
                    dx = current_x - swipe_start_x  # Horizontal movement
                    dy = current_y - swipe_start_y  # Vertical movement

                    # Detect if a swipe gesture is happening
                    if abs(dx) > swipe_threshold and abs(dx) > abs(dy):  # Horizontal swipe
                        mouse_button_down = False  # Cancel button press if it's a swipe
                        if dx > 0:  # Swipe right (to previous page)
                            current_page = ((current_page[0] - 1) % len(pages), 0)
                        else:  # Swipe left (to next page)
                            current_page = ((current_page[0] + 1) % len(pages), 0)

                    elif abs(dy) > swipe_threshold and abs(dy) > abs(dx):  # vertical swipe
                        mouse_button_down = False  # Cancel button press if it's a swipe
                        if dy > 0:  # Swipe down
                            current_page = (current_page[0], (current_page[1] - 1) % len(pages[current_page[0]]))
                        else:  # Swipe up
                            current_page = (current_page[0], (current_page[1] + 1) % len(pages[current_page[0]]))

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_button_down = True
                swipe_start_x, swipe_start_y = event.pos  # Record the start position of the touch

                mouseX, mouseY = event.pos[0], event.pos[1]

                if FLIP:
                    mouseY = SCREEN_HEIGHT - mouseY

                if event.button == 1:  # Left mouse button
                    mouse_button_down = True

                    if pages[current_page[0]][current_page[1]] == "RPM":

                        # Check for collision with increase rectangle
                        if mouseX < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.2+25 and mouseY < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.3:
                            RPM_MAX += 100  # Increase RPM_MAX by 100

                            if RPM_MAX > 50000:
                                RPM_MAX = 50000

                            # Save the new max horsepower data
                            save_rpm(RPM_MAX,SHIFT)

                        # Check for collision with decrease rectangle
                        elif mouseX < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.2+25 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
                            RPM_MAX -= 100  # Decrease RPM_MAX by 100
                            if RPM_MAX == 0:
                                RPM_MAX = 100

                            if SHIFT > RPM_MAX:
                                SHIFT = RPM_MAX

                            # Save the new max horsepower data
                            save_rpm(RPM_MAX,SHIFT)

                        # Check for collision with increase rectangle
                        elif mouseX < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7-25 and mouseY < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.3:
                            SHIFT += 100  # Increase SHIFT by 100

                            if SHIFT > RPM_MAX:
                                SHIFT = RPM_MAX

                            # Save the new max horsepower data
                            save_rpm(RPM_MAX,SHIFT)

                        # Check for collision with decrease rectangle
                        elif mouseX < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7-25 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
                            SHIFT -= 100  # Decrease SHIFT by 100

                            if SHIFT == 0:
                                SHIFT = 100

                            # Save the new max horsepower data
                            save_rpm(RPM_MAX,SHIFT)

                    elif pages[current_page[0]][current_page[1]] == "Settings":

                        # Check for collision with optimize rectangle
                        if mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.42 and mouseY > SCREEN_HEIGHT*.32:
                            if OPTIMIZE:
                                OPTIMIZE = False
                            else:
                                OPTIMIZE = True

                        # Check for collision with flip rectangle
                        elif mouseX < SCREEN_WIDTH//2 + SCREEN_WIDTH*.05 and mouseX > SCREEN_WIDTH//2 - SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
                            if FLIP:
                                FLIP = False
                            else:
                                FLIP = True

                        # Check for collision with delay rectangle
                        elif mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.54 and mouseY > SCREEN_HEIGHT*.44:
                            if DELAY:
                                DELAY = False
                            else:
                                DELAY = True

                        # Check for collision with decrease rectangle
                        elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
                            BRIGHTNESS = decrease_brightness()                            
                        
                        # Check for collision with increase rectangle
                        elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
                            BRIGHTNESS = increase_brightness()

                    elif pages[current_page[0]][current_page[1]] == "Trouble":

                        # Check for collision with exit rectangle
                        if not CLEAR: # To prevent multiple clears
                            if mouseX < SCREEN_WIDTH//2 + SCREEN_WIDTH*.06 and mouseX > SCREEN_WIDTH//2 - SCREEN_WIDTH*.06 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
                                CLEAR = True

                    elif pages[current_page[0]][current_page[1]] == "Info":

                        # Check for collision with exit rectangle
                        if mouseX < SCREEN_WIDTH//2 + SCREEN_WIDTH*.05 and mouseX > SCREEN_WIDTH//2 - SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
                            logging = False
                            exit_text = "Exiting..."
                        
                        # Check for collision with update rectangle
                        elif mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.21 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.09 and mouseY < SCREEN_HEIGHT*.42 and mouseY > SCREEN_HEIGHT*.32:
                            if wifi:
                                logging = False
                                exit_text = "Wifi Update"

                    elif pages[current_page[0]][current_page[1]] == "Custom":

                        # Check for collision with shift light rectangle
                        if mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
                            if SHIFT_LIGHT:
                                SHIFT_LIGHT = False
                            else:
                                SHIFT_LIGHT = True

                skip = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_button_down = False

        # If holding down button
        if mouse_button_down:
            if not skip:
                mouseX, mouseY = pygame.mouse.get_pos()

                if pages[current_page[0]][current_page[1]] == "RPM":

                    # Check for collision with increase rectangle
                    if mouseX < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.2+25 and mouseY < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.3:
                        RPM_MAX += 100  # Increase RPM_MAX by 100

                        if RPM_MAX > 50000:
                            RPM_MAX = 50000

                        # Save the new max horsepower data
                        save_rpm(RPM_MAX,SHIFT)

                    # Check for collision with decrease rectangle
                    elif mouseX < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.2+25 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
                        RPM_MAX -= 100  # Decrease RPM_MAX by 100
                        if RPM_MAX == 0:
                            RPM_MAX = 100

                        if SHIFT > RPM_MAX:
                            SHIFT = RPM_MAX

                        # Save the new max horsepower data
                        save_rpm(RPM_MAX,SHIFT)

                    # Check for collision with increase rectangle
                    elif mouseX < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7-25 and mouseY < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.3:
                        SHIFT += 100  # Increase SHIFT by 100

                        if SHIFT > RPM_MAX:
                            SHIFT = RPM_MAX

                        # Save the new max horsepower data
                        save_rpm(RPM_MAX,SHIFT)

                    # Check for collision with decrease rectangle
                    elif mouseX < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7-25 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
                        SHIFT -= 100  # Decrease SHIFT by 100

                        if SHIFT == 0:
                            SHIFT = 100

                        # Save the new max horsepower data
                        save_rpm(RPM_MAX,SHIFT)

                if pages[current_page[0]][current_page[1]] == "Settings":

                    # Check for collision with decrease rectangle
                    if mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
                        BRIGHTNESS = decrease_brightness()                            
                    
                    # Check for collision with increase rectangle
                    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
                        BRIGHTNESS = increase_brightness()

                time.sleep(.05)
            skip = False

        with open("Data/info.txt", "w") as file:
            file.write(str(current_page[0]))
            file.write(f'\n{str(current_page[1])}')
            file.write(f'\n{str(int(SHIFT_LIGHT))}')
            file.write(f'\n{str(int(DELAY))}')
            file.write(f'\n{str(int(OPTIMIZE))}')
        
        if DEV:
            # Set random variables for testing purposes
            rpm = random.randint(max(0,rpm-50), min(rpm+60,RPM_MAX))
            speed = random.uniform(max(0,speed-10), min(speed+100,80))* 0.621371
            maf = round(maf,0)
            maf = random.randint(max(1,maf-1), min(maf+1,80))
            mpg = calculate_mpg(speed, maf)
            if fuel_level<=0:
                fuel_level=100
            fuel_level -= .1
            voltage = random.uniform(max(14,voltage-.1), min(voltage+.1,15))
            air_temp = random.randint(0,50)
            if CLEAR:
                CLEARED = random.randint(1,3)
                CLEAR = False

            if CLEARED != 1:
                codes = [("P0104", "Mass or Volume Air Flow Circuit Intermittent"),("B0123", "This is a very long message to simulate a long description hoping for it to be cut off properly to have a consistent message flow."),("C0123", f"{' '.join(['*' for i in range(60)])}"), ("D0123", ""), ("E0123", "")]
            else:
                codes = []

        # Clear the screen
        screen.fill(BLACK)

        # Draw page indicators (circles)
        circle_radius = 8
        circle_spacing = 7

        # Calculate total width occupied by circles
        total_circle_width = (len(pages)) * (2 * circle_radius + circle_spacing) + circle_spacing + (2*circle_radius)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = SCREEN_HEIGHT - circle_radius - circle_spacing

        for i, page in enumerate(pages):
            # if page != 'Off':
            color = FONT_COLOR if i == current_page[0] else BLACK
            pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius + 4)
            pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 2)
            pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
            circle_x += 2 * (circle_radius + circle_spacing)

        # Calculate total height occupied by circles
        total_circle_height = (len(pages[0])) * (2 * circle_radius + circle_spacing) + circle_spacing + (2 * circle_radius)

        # Calculate starting position to center vertically
        start_y = (SCREEN_HEIGHT - total_circle_height) // 2
        circle_x = SCREEN_WIDTH - circle_radius - circle_spacing
        circle_y = start_y + circle_radius + circle_spacing

        for i, page in enumerate(pages[current_page[0]]):
            color = FONT_COLOR if i == current_page[1] else BLACK
            pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius + 4)
            pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 2)
            pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
            circle_y += 2 * (circle_radius + circle_spacing)

        try:
            if pages[current_page[0]][current_page[1]] == "RPM":
                draw_text(screen, "RPM Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

                # Draw RPM section
                draw_text(screen, "RPM", font_medium_clean, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
                draw_text(screen, str(rpm), font_large, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)
                draw_text(screen, "Max", font_small_clean, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2)
                draw_text(screen, str(RPM_MAX), font_medium, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2 +40)
                draw_text(screen, "Shift", font_small_clean, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2)
                draw_text(screen, str(SHIFT), font_medium, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2 +40)

                pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
                pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

                draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
                draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)

                pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
                pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

                draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
                draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)

            elif pages[current_page[0]][current_page[1]] == "Main":
                screen.fill(BACKGROUND_COLOR)

                # Calculate the width of the filled portion based on percentage
                fuel_width = math.floor((SCREEN_WIDTH*.7663) * fuel_level/100)

                # Draw the filled portion
                if fuel_level > 75:
                    fuel_color = GREEN
                elif fuel_level <=75 and fuel_level > 50:
                    fuel_color = YELLOW
                elif fuel_level <=50 and fuel_level > 30:
                    fuel_color = ORANGE
                else:
                    fuel_color = RED
                
                pygame.draw.rect(screen, fuel_color, (SCREEN_WIDTH*.22, SCREEN_HEIGHT*.75, fuel_width, SCREEN_HEIGHT*.22))

                # Calculate the percentage of RPM relative to RPM_MAX
                rpm_percentage = min(1.0, rpm / RPM_MAX)  # Ensure it's between 0 and 1
                
                # Calculate the height of the filled portion based on percentage
                rpm_width = math.floor((SCREEN_WIDTH*.98) * rpm_percentage)

                # Draw the filled portion
                rpm_color = GREEN if rpm<SHIFT else RED

                # Draw the shift line
                shiftLineColor = RED if rpm<SHIFT else BLACK
                shift_line_x = SCREEN_WIDTH - (SHIFT / RPM_MAX) * SCREEN_WIDTH*.99

                pygame.draw.rect(screen, rpm_color, (SCREEN_WIDTH * 0.01, 0, rpm_width, SCREEN_HEIGHT*.25))
                pygame.draw.line(screen, shiftLineColor, (SCREEN_WIDTH-shift_line_x, 0), (SCREEN_WIDTH-shift_line_x, SCREEN_HEIGHT*.25), 5)

                screen.blit(curveOut, ((SCREEN_WIDTH - curveOut.get_width())//2, (SCREEN_HEIGHT - curveOut.get_height())//2))
                screen.blit(curveIn, ((SCREEN_WIDTH - curveIn.get_width())//2, (SCREEN_HEIGHT - curveIn.get_height())//2))
                pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT*.25, SCREEN_WIDTH * .22, SCREEN_HEIGHT))
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH-SCREEN_WIDTH*.22, SCREEN_HEIGHT*.25, SCREEN_WIDTH, SCREEN_HEIGHT*.5))
                pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH*.12, SCREEN_HEIGHT*.15, SCREEN_WIDTH*.75, SCREEN_HEIGHT*.7))
                
                draw_text(screen, f"{round(fuel_level,1)}%", font_medium, FONT_COLOR, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.93)

                draw_text(screen, f"{rpm}", font_xlarge, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT//2)
                draw_text(screen, "RPM", font_small_clean, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT*.7)

                if not OPTIMIZE:
                    draw_text(screen,f"{(round(mpg, 2))}", font_medlar, FONT_COLOR, SCREEN_WIDTH *.13, SCREEN_HEIGHT // 2)
                    draw_text(screen, "MPG", font_small_clean, FONT_COLOR, SCREEN_WIDTH *.13, SCREEN_HEIGHT // 2+50)

                    draw_text(screen, f"{int(round(speed,0))}", font_medlar, FONT_COLOR, SCREEN_WIDTH *.87, SCREEN_HEIGHT // 2)
                    draw_text(screen, "MPH", font_small_clean, FONT_COLOR, SCREEN_WIDTH *.87, SCREEN_HEIGHT // 2+50)

                if not OPTIMIZE:
                    draw_text(screen, f"{round((air_temp*(9/5))+32,1)}F", font_medium, FONT_COLOR, SCREEN_WIDTH*.7, SCREEN_HEIGHT - SCREEN_HEIGHT*.15)
                    draw_text(screen, f"{round(voltage,1)} v", font_medium, FONT_COLOR, SCREEN_WIDTH*.3, SCREEN_HEIGHT - SCREEN_HEIGHT*.15)

                if SHIFT_LIGHT:
                    # Draw shift indicators (circles)
                    circle_radius = 22
                    circle_spacing = 5

                    total_circle_width = 12 * (2 * circle_radius + 2 * circle_spacing)

                    # Calculate starting position to center horizontally
                    start_x = (SCREEN_WIDTH - total_circle_width) // 2
                    circle_x = start_x + circle_radius + circle_spacing
                    circle_y = circle_radius + circle_spacing+SCREEN_HEIGHT*.15

                    # Colors for each light
                    light_colors = [GREEN, GREEN, GREEN, GREEN, YELLOW, YELLOW, YELLOW, YELLOW, RED, RED, RED, RED]

                    for i in range(len(light_colors)):
                        color = light_colors[i]

                        pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius )
                        pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius -1)
                        
                        blink_pattern = (internal_clock == .1) or (internal_clock == .3)

                        if rpm > SHIFT - (((len(light_colors)+2) - i) * 100):
                            if rpm > SHIFT and blink_pattern:
                                pygame.draw.circle(screen, PURPLE, (circle_x, circle_y), circle_radius)
                            elif rpm > SHIFT and not blink_pattern:
                                pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius)
                            elif rpm < SHIFT and rpm > SHIFT - 200:
                                pygame.draw.circle(screen, PURPLE, (circle_x, circle_y), circle_radius)
                            else:
                                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                            
                        circle_x += 2 * (circle_radius + circle_spacing)

            elif pages[current_page[0]][current_page[1]] == "Settings":
                draw_text(screen, "General Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

                pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH // 2 - SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
                draw_text(screen, "FLIP", font_small_clean, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)
            
                pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.50, SCREEN_HEIGHT*.20, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
                pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.70, SCREEN_HEIGHT*.20, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

                draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.25)
                draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.25)
                draw_text(screen, f"{int(round((BRIGHTNESS/255)*100,0))}%", font_small, FONT_COLOR, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
                draw_text(screen, "Brightness", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

                pygame.draw.rect(screen, GREEN if OPTIMIZE else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.32, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
                draw_text(screen, "On" if OPTIMIZE else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
                draw_text(screen, "Optimize readings", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

                pygame.draw.rect(screen, GREEN if DELAY else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.44, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
                draw_text(screen, "On" if DELAY else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)
                draw_text(screen, "Delay readings", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)

            elif pages[current_page[0]][current_page[1]] == "Trouble":
                draw_text(screen, "Trouble Codes", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)
                
                if len(codes):
                    if CLEARED:
                        if CLEARED == 2:
                            error_text = "Attempting to clear codes..."
                        else:
                            error_text = "Turn off the engine before clearing codes!"
                        draw_text(screen, error_text, font_small_clean, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)
                    else:
                        pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - SCREEN_WIDTH*.06, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.12, SCREEN_HEIGHT*.1))
                        draw_text(screen, "Clear", font_small_clean, BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)

                    code_offset = 0
                    max_width = SCREEN_WIDTH * 0.8
                    cutoff = 100 # Character limit to limit to max of 2 lines
                    code_count = 0
                    max_codes = 3
                    for code in codes:
                        # Make sure there is only a certain amount of codes displaying
                        if code_count == max_codes:
                            num_codes_left = len(codes) - code_count

                            # Add plural
                            code_text = 'Code'
                            if num_codes_left > 1:
                                code_text += 's'

                            # Display how many codes are in list
                            draw_text(screen, f"{num_codes_left} More {code_text} Remaining", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.75)
                            break

                        # Fit the text into 2 lines
                        if len(code[1]) > cutoff:
                            code = (code[0], code[1][:cutoff-3]+'. . .')

                        # If there is no description
                        if code[1] == "":
                            code = (code[0], "Unknown")
                        
                        # Draw the trouble code and description with wrapping
                        draw_text(screen, f"{code[0]}: {code[1]}", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.2 + SCREEN_HEIGHT*code_offset, max_width=max_width)
                        
                        # Adjust the offset for the next code
                        code_offset += 0.1 + (font_small.get_height() / SCREEN_HEIGHT)
                        code_count += 1
                else:
                    draw_text(screen, f"{'Trouble codes have been cleared, Please restart car' if CLEARED else 'No trouble codes detected'}", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.25)

            elif pages[current_page[0]][current_page[1]] == "Info":
                draw_text(screen, "System Information", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

                draw_text(screen, f"Version: {SYSTEM_VERSION}", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.2)
            
                pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
                draw_text(screen, "Exit", font_small_clean, BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)

                pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.09, SCREEN_HEIGHT*.32, SCREEN_WIDTH*.12, SCREEN_HEIGHT*.1))
                draw_text(screen, "Update", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
                draw_text(screen, "Wifi Update", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

            elif pages[current_page[0]][current_page[1]] == "Custom":
                draw_text(screen, "Customization Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

                pygame.draw.rect(screen, GREEN if SHIFT_LIGHT else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
                draw_text(screen, "On" if SHIFT_LIGHT else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
                draw_text(screen, "Shift lights", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

            elif pages[current_page[0]][current_page[1]] == "Off":
                screen.fill(BLACK)
        except IndexError:
            current_page = (current_page[0],0)

        if FLIP:
            flipped_screen = pygame.transform.flip(screen, False, True)
            screen.blit(flipped_screen, (0, 0))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

        interval = 0.1
        if DEV:
            interval += .0215
        internal_clock = round((internal_clock + interval) % .4, 1)
        time.sleep(interval)

    print(exit_text)

    if not DEV:
        # Stop and close the connection
        connection.stop()
        connection.close()

        # Shutting down
        subprocess.run("sudo shutdown -h now", shell=True, capture_output=True, text=True)

if __name__ == "__main__":
    main()
