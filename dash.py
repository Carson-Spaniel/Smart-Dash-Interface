import pygame
import obd
import time
import random
import math

# Environment Variables
DEV = True
PI = False

# Initialize Pygame
pygame.init()

# Screen dimensions for a landscape 4.3-inch display
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
FPS = 30

# Colors
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 150, 255)

FONT_COLOR = WHITE

# Fonts
font_xlarge = pygame.font.Font("./digital-7.ttf", 200)
font_large = pygame.font.Font("./digital-7.ttf", 120)
font_medlar = pygame.font.Font("./digital-7.ttf", 100)
font_medium = pygame.font.Font("./digital-7.ttf", 48)
font_small = pygame.font.Font("./digital-7.ttf", 36)

connect = False

if not DEV:
    try: 
        for i in range(3):
            print('\nAttempting to connect...\n')

            if PI:
                # The Bluetooth port for RFCOMM on Raspberry Pi
                port = "/dev/rfcomm0"
            else:
                # Port for the Bluetooth connection on my laptop
                port =  "COM5"
                
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
        print('\nExiting...')
        exit()

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
    with open("RPM.txt", "w") as file:
        file.write(f"{RPM_MAX},{SHIFT}")

# Function to load max horsepower data from a file
def load_rpm():
    try:
        with open("RPM.txt", "r") as file:
            data = file.read().split(",")
            max = int(data[0])
            shift = int(data[1])
    except Exception as e:
        print(e)
        max = 8000
        shift = 6500

    return max, shift

RPM_MAX,SHIFT = load_rpm()

# Function to calculate MPG
def calculate_mpg(speed, maf):
    if speed == 0:
        return 0
    gph = (maf / 14.7) * 0.746  # grams per hour to gallons per hour
    mpg = speed / gph
    return round(mpg, 1)

# Function to draw text on screen
def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to display Chevrolet logo animation
def display_logo(screen):
    logo = pygame.image.load("chevy.jpg").convert_alpha()
    logo_rect = logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Animation variables
    rotation_angle = 0
    scale = 0.2
    animation_duration = 5  # 5 seconds
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

        scale += 0.004

        pygame.time.Clock().tick(FPS)

# Main function for the Pygame interface
def main():
    if not PI:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption("Smart Dash")
    clock = pygame.time.Clock()

    # Initialize variables
    pages = ["Main" , "RPM", "Settings"] #,"MPG", "Off"
    current_page = 0
    mpg_history = []
    last_mile_mpg = 0.0
    last_mile_distance = 0.0
    internal_clock = 2.8000000000000003
    global RPM_MAX
    global SHIFT
    FLIP = False
    display = 1
    curve = pygame.image.load("round2.png").convert_alpha()
    curveOut = pygame.transform.scale(curve, (curve.get_width() * 1.8, curve.get_height() * 1.6))
    curveIn = pygame.transform.scale(curve, (curve.get_width() * 1.4, curve.get_height() * 1.1))

    # Load the last visited page
    try:
        with open("last_visited_page.txt", "r") as file:
            current_page = int(file.read())
            if current_page < 0 or current_page >= len(pages):
                current_page = 0
    except Exception:
        current_page = 0

    if not DEV:
        # Display Chevrolet logo for 5 seconds
        display_logo(screen)

    if DEV:
        rpm = 650
        fuel_level = random.randint(0,100)
        speed = 0
        maf = 6
        voltage = 15.5
    
    logging = True
    while logging:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos[0], event.pos[1]
                if FLIP:
                    # mouseX = SCREEN_WIDTH - mouseX
                    mouseY = SCREEN_HEIGHT - mouseY
                if event.button == 1:  # Left mouse button
                    # Check top left corner for page change
                    if mouseX < SCREEN_WIDTH // 10 and mouseY < SCREEN_HEIGHT // 10:
                        current_page = (current_page - 1) % len(pages)
                    # Check top right corner for page change
                    elif mouseX > SCREEN_WIDTH - SCREEN_WIDTH // 10 and mouseY < SCREEN_HEIGHT // 10:
                        current_page = (current_page + 1) % len(pages)
                    else:
                        if pages[current_page] == "RPM":
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
                        if pages[current_page] == "Settings":
                            # Check for collision with flip rectangle
                            if mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.05 and mouseX > SCREEN_WIDTH // 2 - SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
                                if FLIP:
                                    FLIP = False
                                else:
                                    FLIP = True

                            # Check for collision with flip rectangle
                            elif mouseX < SCREEN_WIDTH*.3 + SCREEN_WIDTH*.05 and mouseX > SCREEN_WIDTH*.3 - SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
                                logging = False

                            # Check for collision with decrease rectangle
                            elif mouseX < SCREEN_WIDTH * 0.35 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.35 and mouseY < SCREEN_HEIGHT*.12+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.12:
                                decrease_brightness()                            
                            
                            # Check for collision with increase rectangle
                            elif mouseX < SCREEN_WIDTH * 0.55 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.55 and mouseY < SCREEN_HEIGHT*.12+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.12:
                                increase_brightness()
                                
        if DEV:
            rpm = random.randint(max(0,rpm-50), min(rpm+150,RPM_MAX))
            speed = random.uniform(max(0,speed-10), min(speed+100,80))* 0.621371
            maf = random.randint(max(1,maf-1), min(maf+1,80))
            mpg = calculate_mpg(speed, maf)
            if fuel_level<=0:
                fuel_level=100
            fuel_level -= .1
            voltage = random.uniform(max(14,voltage-.1), min(voltage+.1,15))
            air_temp = random.randint(0,50)
        else:
            # Query for RPM and Torque
            response_rpm = connection.query(obd.commands.RPM)
            response_fuel_level = connection.query(obd.commands.FUEL_LEVEL)
            response_speed = connection.query(obd.commands.SPEED)  # Vehicle speed
            response_maf = connection.query(obd.commands.MAF)      # Mass Air Flow
            response_voltage = connection.query(obd.commands.CONTROL_MODULE_VOLTAGE)
            response_air_temp = connection.query(obd.commands.AMBIANT_AIR_TEMP)

            if not response_speed.is_null() and not response_maf.is_null():
                speed = response_speed.value.to('mile/hour').magnitude
                maf = response_maf.value.to('gram/second').magnitude
                mpg = calculate_mpg(speed, maf)

            if not response_rpm.is_null():
                rpm = int(round(response_rpm.value.magnitude,0))

            if not response_fuel_level.is_null():
                fuel_level = response_fuel_level.value.magnitude

            if not response_voltage.is_null():
                voltage = response_voltage.value.magnitude

            if not response_air_temp.is_null():
                air_temp = response_air_temp.value.magnitude

        if speed > 0:
            last_mile_distance += speed / 3600  # speed in miles per second, convert to hours
            mpg_history.append(mpg)

        # If the last mile is completed
        if last_mile_distance >= 1.0:

            # Calculate average MPG for the last mile
            last_mile_mpg = sum(mpg_history) / len(mpg_history)

            # Reset for the next mile
            last_mile_distance = 0.0
            mpg_history = []

        # Clear the screen
        screen.fill(BLACK)

        # Draw page buttons
        draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH*.02, SCREEN_HEIGHT * .05)
        draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH -SCREEN_WIDTH*.02, SCREEN_HEIGHT * .05)

        if display == 0:
            # Calculate the percentage of RPM relative to RPM_MAX
            rpm_percentage = min(1.0, rpm / RPM_MAX)  # Ensure it's between 0 and 1
            
            # Calculate the height of the filled portion based on percentage
            filled_height = math.floor((SCREEN_HEIGHT*.88) * rpm_percentage)

            # Draw the filled portion
            color = GREEN if rpm<SHIFT else RED
            pygame.draw.rect(screen, color, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT - filled_height, SCREEN_WIDTH * 0.2, filled_height))
            
            # Draw the shift line
            shiftLineColor = RED if rpm<SHIFT else BLACK
            shift_line_y = SCREEN_HEIGHT - (SHIFT / RPM_MAX) * SCREEN_HEIGHT*.88
            pygame.draw.line(screen, shiftLineColor, (SCREEN_WIDTH * 0.8, shift_line_y), (SCREEN_WIDTH, shift_line_y), 5)

            pygame.draw.line(screen, BLACK, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.12+2), (SCREEN_WIDTH, SCREEN_HEIGHT*.12+2), 4)
            pygame.draw.line(screen, BLACK, (SCREEN_WIDTH * 0.8+2, SCREEN_HEIGHT*.12), (SCREEN_WIDTH * 0.8+2, SCREEN_HEIGHT), 4)

            pygame.draw.line(screen, FONT_COLOR, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.12), (SCREEN_WIDTH, SCREEN_HEIGHT*.12), 2)
            pygame.draw.line(screen, FONT_COLOR, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.12), (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT), 2)

            # Calculate the height of the filled portion based on percentage
            fuel_height = math.floor((SCREEN_HEIGHT*.8) * fuel_level/100)

            # Draw the filled portion
            if fuel_level > 75:
                fuel_color = GREEN
            elif fuel_level <=75 and fuel_level > 50:
                fuel_color = YELLOW
            elif fuel_level <=50 and fuel_level > 30:
                fuel_color = ORANGE
            else:
                fuel_color = RED
            
            draw_text(screen, f"{round(fuel_level,1)}%", font_medium, FONT_COLOR, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.15)
            pygame.draw.rect(screen, fuel_color, (0, SCREEN_HEIGHT - fuel_height, SCREEN_WIDTH * 0.2, fuel_height))

            pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT*.2+2), (SCREEN_WIDTH*.2, SCREEN_HEIGHT*.2+2), 4)
            pygame.draw.line(screen, BLACK, (SCREEN_WIDTH * 0.2-2, SCREEN_HEIGHT*.2), (SCREEN_WIDTH * 0.2-2, SCREEN_HEIGHT), 4)

            pygame.draw.line(screen, FONT_COLOR, (0, SCREEN_HEIGHT*.2), (SCREEN_WIDTH*.2, SCREEN_HEIGHT*.2), 2)
            pygame.draw.line(screen, FONT_COLOR, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT*.2), (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT), 2)

            # Draw shift indicators (circles)
            circle_radius = 22
            circle_spacing = 5

            total_circle_width = 12 * (2 * circle_radius + 2 * circle_spacing)

            # Calculate starting position to center horizontally
            start_x = (SCREEN_WIDTH - total_circle_width) // 2
            circle_x = start_x + circle_radius + circle_spacing
            circle_y = circle_radius + circle_spacing

            # Colors for each light
            light_colors = [GREEN, GREEN, GREEN, GREEN, YELLOW, YELLOW, YELLOW, YELLOW, RED, RED, RED, RED]

            for i in range(len(light_colors)):
                color = light_colors[i]

                pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius )
                pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius -1)
                blink_pattern = internal_clock % .4 > .2
                
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

        # Draw page indicators (circles)
        circle_radius = 8
        circle_spacing = 10

        # Calculate total width occupied by circles
        total_circle_width = (len(pages)) * (2 * circle_radius + circle_spacing) + circle_spacing + (2*circle_radius)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = SCREEN_HEIGHT - circle_radius - circle_spacing

        for i, page in enumerate(pages):
            if page != 'Off':
                color = FONT_COLOR if i == current_page else BLACK
                pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius + 4)
                pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 2)
                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                circle_x += 2 * (circle_radius + circle_spacing)

        if pages[current_page] == "RPM":
            # Draw RPM section
            draw_text(screen, "RPM", font_medium, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
            draw_text(screen, str(rpm), font_large, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)
            draw_text(screen, "Max", font_small, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2)
            draw_text(screen, str(RPM_MAX), font_medium, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2 +40)
            draw_text(screen, "Shift", font_small, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2)
            draw_text(screen, str(SHIFT), font_medium, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2 +40)

            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

            draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
            draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)

            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

            draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
            draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)

        elif pages[current_page] == "Main":
            if display == 0:
                # Draw voltage and speed
                draw_text(screen, f"{round(voltage,1)}", font_medium, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT - SCREEN_HEIGHT*.1)
                draw_text(screen, f"{int(round(speed,0))}", font_medium, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT - SCREEN_HEIGHT*.1)

                draw_text(screen, "Volts", font_small, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT - SCREEN_HEIGHT*.2)
                draw_text(screen, "MPH", font_small, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT - SCREEN_HEIGHT*.2)

                draw_text(screen, f"{round(last_mile_mpg,1)}", font_medium, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT*.2)
                draw_text(screen, "MPG", font_small, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT*.3)
                draw_text(screen, f"{round(last_mile_distance*100,2)}%", font_small, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT*.4)

                draw_text(screen, f"{round((air_temp*(9/5))+32,1)}F", font_medium, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT*.2)
                # draw_text(screen, "Temp", font_small, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT*.3)

                # Draw RPM and MPG on separate lines
                draw_text(screen, "RPM", font_medium, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
                draw_text(screen, "Instant MPG", font_medium, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
                draw_text(screen, f"{rpm}", font_large, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 70)
                draw_text(screen, str(round(mpg, 2)), font_large, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110)
            elif display == 1:
                screen.fill(BLUE)

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
                draw_text(screen, "RPM", font_small, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT*.7)

                draw_text(screen,f"{(round(mpg, 2))}", font_medlar, FONT_COLOR, SCREEN_WIDTH *.13, SCREEN_HEIGHT // 2)
                draw_text(screen, "MPG", font_small, FONT_COLOR, SCREEN_WIDTH *.13, SCREEN_HEIGHT // 2+50)

                draw_text(screen, f"{int(round(speed,0))}", font_medlar, FONT_COLOR, SCREEN_WIDTH *.87, SCREEN_HEIGHT // 2)
                draw_text(screen, "MPH", font_small, FONT_COLOR, SCREEN_WIDTH *.87, SCREEN_HEIGHT // 2+50)

                draw_text(screen, f"{round((air_temp*(9/5))+32,1)}F", font_medium, FONT_COLOR, SCREEN_WIDTH*.7, SCREEN_HEIGHT - SCREEN_HEIGHT*.15)
                draw_text(screen, f"{round(voltage,1)} v", font_medium, FONT_COLOR, SCREEN_WIDTH*.3, SCREEN_HEIGHT - SCREEN_HEIGHT*.15)

                # Draw page buttons
                draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH*.02, SCREEN_HEIGHT * .05)
                draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH -SCREEN_WIDTH*.02, SCREEN_HEIGHT * .05)

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
                    blink_pattern = internal_clock % .4 > .2
                    
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

        elif pages[current_page] == "Settings":
            pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH // 2 - SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
            draw_text(screen, "FLIP", font_small, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)
        
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.35, SCREEN_HEIGHT*.12, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.12, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

            draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.35+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.12+SCREEN_HEIGHT*.05)
            draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.55+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.12+SCREEN_HEIGHT*.05)
            draw_text(screen, f"{int(round((BRIGHTNESS/255)*100,0))}%", font_small, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.12+SCREEN_HEIGHT*.05)
            draw_text(screen, "Brightness", font_small, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.25)
            
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH*.3 - SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
            draw_text(screen, "Exit", font_small, BLACK, SCREEN_WIDTH*.3, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)
        
        elif pages[current_page] == "Off":
            screen.fill(BLACK)

        with open("last_visited_page.txt", "w") as file:
            file.write(str(current_page))

        if FLIP:
            flipped_screen = pygame.transform.flip(screen, False, True)
            screen.blit(flipped_screen, (0, 0))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

        if DEV:
            internal_clock += .20
            time.sleep(.1)
        else:
            internal_clock += .10

    print("Exiting...")

    if not DEV:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()