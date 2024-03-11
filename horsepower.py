import pygame
import obd
import time
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions for a landscape 3.5-inch display
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320
FPS = 30

# Colors
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RPM_MAX = 8000
SHIFT = 6500

# Fonts
font_large = pygame.font.Font(None, 120)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

ports = obd.scan_serial()
print("Available ports:", ports)

# Connect to the OBD-II adapter
connection = obd.OBD()

# Print a message indicating connection
if connection.is_connected():
    print("Connected to OBD-II adapter. Ready to log data.")
else:
    print("Could not connect to OBD-II adapter. Exiting...")
    exit()

# Function to save max horsepower data to a file
def save_max_horsepower(max_horsepower, max_horsepower_rpm):
    with open("max_horsepower.txt", "w") as file:
        file.write(f"{max_horsepower},{max_horsepower_rpm}")

# Function to load max horsepower data from a file
def load_max_horsepower():
    try:
        with open("max_horsepower.txt", "r") as file:
            data = file.read().split(",")
            max_horsepower = float(data[0])
            max_horsepower_rpm = int(data[1])
    except Exception:
        max_horsepower = 0
        max_horsepower_rpm = 0

    return max_horsepower, max_horsepower_rpm

# Function to calculate horsepower
def calculate_horsepower(torque, rpm):
    return (torque * rpm) / 5252

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

        pygame.display.flip()

        scale += 0.004

        pygame.time.Clock().tick(FPS)

# Main function for the Pygame interface
def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Horsepower and RPM Display")
    clock = pygame.time.Clock()

    pages = ["RPM", "Horsepower", "Both", "Off"]
    current_page = 0

    # Load the last visited page
    try:
        with open("last_visited_page.txt", "r") as file:
            current_page = int(file.read())
            if current_page < 0 or current_page >= len(pages):
                current_page = 0
    except FileNotFoundError:
        current_page = 0

    logging = True

    # Display Chevrolet logo for 5 seconds
    # display_logo(screen)

    # Load the initial maximum horsepower and RPM
    max_horsepower, max_horsepower_rpm = load_max_horsepower()

    rpm = 650
    while logging:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if the click was on the right half of the screen
                    if event.pos[0] > SCREEN_WIDTH / 2:
                        current_page = (current_page + 1) % len(pages)
                    else:  # Click on the left half of the screen
                        current_page = (current_page - 1) % len(pages)

        # Query for RPM and Torque
        cmd_rpm = obd.commands.RPM
        cmd_torque = obd.commands.ENGINE_LOAD  # Torque can be estimated from ENGINE_LOAD
        response_rpm = connection.query(cmd_rpm)
        response_torque = connection.query(cmd_torque)

        if not response_rpm.is_null() and not response_torque.is_null():
            rpm = response_rpm.value.magnitude
            torque = response_torque.value.magnitude

        # rpm = random.randint(max(0,rpm-200), min(rpm+270,RPM_MAX))
        # torque = random.randint(200, 250)

        horsepower = calculate_horsepower(torque, rpm)

        # Update maximum horsepower and RPM if current is greater
        if horsepower > max_horsepower:
            max_horsepower = horsepower
            max_horsepower_rpm = rpm
            # Save the new max horsepower data
            save_max_horsepower(max_horsepower, max_horsepower_rpm)

        # Clear the screen
        screen.fill(BLACK)

        # Draw page indicators (circles)
        circle_radius = 5
        circle_spacing = 10

        # Calculate total width occupied by circles
        total_circle_width = (len(pages)) * (2 * circle_radius + circle_spacing) + circle_spacing + (2*circle_radius)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = SCREEN_HEIGHT - circle_radius - circle_spacing

        # Calculate the percentage of RPM relative to RPM_MAX
        rpm_percentage = min(1.0, rpm / RPM_MAX)  # Ensure it's between 0 and 1
        
        # Calculate the height of the filled portion based on percentage
        filled_height = math.floor((SCREEN_HEIGHT*.8) * rpm_percentage)

        # Draw the filled portion
        color = GREEN if rpm<SHIFT else RED
        pygame.draw.rect(screen, color, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT - filled_height, SCREEN_WIDTH * 0.2, filled_height))
        
        # Draw the shift line
        shiftLineColor = RED if rpm<SHIFT else BLACK
        shift_line_y = SCREEN_HEIGHT - (SHIFT / RPM_MAX) * SCREEN_HEIGHT*.8
        pygame.draw.line(screen, shiftLineColor, (SCREEN_WIDTH * 0.8, shift_line_y), (SCREEN_WIDTH, shift_line_y), 5)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.2), (SCREEN_WIDTH, SCREEN_HEIGHT*.2), 2)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.2), (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT), 2)

        for i, page in enumerate(pages):
            if page != 'Off':
                color = WHITE if i == current_page else BLACK
                pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius + 4)
                pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 2)
                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                circle_x += 2 * (circle_radius + circle_spacing)

        # Draw page indicators (circles)
        circle_radius = 22
        circle_spacing = 6

        total_circle_width = 8 * (2 * circle_radius + 2 * circle_spacing)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = circle_radius + circle_spacing #+ 20

        # Colors for each light
        light_colors = [YELLOW, YELLOW, ORANGE, ORANGE, RED, RED, PURPLE, PURPLE]

        for i in range(8):
            color = light_colors[i]

            # Adjust y-coordinate for arch pattern
            # if i < 3:
            #     circle_y -= 5
            # elif i > 5:
            #     circle_y += 5

            pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius + 4)
            pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 2)
            
            if rpm > SHIFT - ((8 - i) * 200):
                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                
            circle_x += 2 * (circle_radius + circle_spacing)

        if pages[current_page] == "RPM":
            # Draw RPM section
            draw_text(screen, "RPM", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
            draw_text(screen, str(rpm), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)

        elif pages[current_page] == "Horsepower":
            # Draw Horsepower section
            draw_text(screen, "Horsepower", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
            draw_text(screen, str(round(horsepower, 2)), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            # Display Max HP and corresponding RPM
            draw_text(screen, f"{str(round(max_horsepower, 2))} @ {max_horsepower_rpm} RPM", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)

        elif pages[current_page] == "Both":
            # Draw RPM and Horsepower on separate lines
            draw_text(screen, "RPM", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, "Horsepower", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
            draw_text(screen, f"{rpm}", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 50)
            draw_text(screen, f"{round(horsepower, 2)}", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90)

        elif pages[current_page] == "Off":
            screen.fill(BLACK)

        with open("last_visited_page.txt", "w") as file:
            file.write(str(current_page))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

        time.sleep(.1)  # Wait for 0.1 second before next iteration

    print("Logging stopped.")

    # Close the connection
    connection.close()

if __name__ == "__main__":
    main()