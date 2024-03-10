import pygame
import obd
import time
import random

# Initialize Pygame
pygame.init()

# Screen dimensions for a landscape 3.5-inch display
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# Connect to the OBD-II adapter
connection = obd.OBD()

# Print a message indicating connection
# if connection.is_connected():
#     print("Connected to OBD-II adapter. Ready to log data.")
# else:
#     print("Could not connect to OBD-II adapter. Exiting...")
#     exit()

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

    logging = True

    # Display Chevrolet logo for 5 seconds
    display_logo(screen)

    # Define the initial maximum horsepower and RPM
    max_horsepower = 0
    max_horsepower_rpm = 0

    while logging:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    current_page = (current_page + 1) % len(pages)

        # # Query for RPM and Torque
        # cmd_rpm = obd.commands.RPM
        # cmd_torque = obd.commands.ENGINE_LOAD  # Torque can be estimated from ENGINE_LOAD
        # response_rpm = connection.query(cmd_rpm)
        # response_torque = connection.query(cmd_torque)

        # if not response_rpm.is_null() and not response_torque.is_null():
        #     rpm = response_rpm.value.magnitude
        #     torque = response_torque.value.magnitude

        rpm = random.randint(1000, 9000)
        torque = random.randint(100, 450)

        horsepower = calculate_horsepower(torque, rpm)

        # Update maximum horsepower and RPM if current is greater
        if horsepower > max_horsepower:
            max_horsepower = horsepower
            max_horsepower_rpm = rpm

        # Clear the screen
        screen.fill(BLACK)

        # Draw page indicators (circles)
        circle_radius = 10
        circle_spacing = 20
        circle_x = circle_radius + circle_spacing
        circle_y = SCREEN_HEIGHT - circle_radius - circle_spacing
        for i, page in enumerate(pages):
            if page != 'Off':
                color = WHITE if i == current_page else BLACK
                pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius + 10)
                pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 5)
                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                circle_x += 2 * (circle_radius + circle_spacing)

        if pages[current_page] == "RPM":
            # Draw RPM section
            draw_text(screen, "RPM", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, str(rpm), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        elif pages[current_page] == "Horsepower":
            # Draw Horsepower section
            draw_text(screen, "Horsepower", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, str(round(horsepower, 2)), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)

            # Display Max HP and corresponding RPM
            draw_text(screen, f"{str(round(max_horsepower, 2))} @ {max_horsepower_rpm} RPM", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

        elif pages[current_page] == "Both":
            # Draw RPM and Horsepower on separate lines
            draw_text(screen, "RPM", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 - 20)
            draw_text(screen, "Horsepower", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)
            draw_text(screen, f"{rpm}", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 30)
            draw_text(screen, f"{round(horsepower, 2)}", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70)

        elif pages[current_page] == "Off":
            screen.fill(BLACK)

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

        time.sleep(.1)  # Wait for 0.1 second before next iteration

    print("Logging stopped.")

    # Close the connection
    connection.close()

if __name__ == "__main__":
    main()