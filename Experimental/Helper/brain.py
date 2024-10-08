import pygame
import math
import time

# Initialize Pygame
pygame.init()

# Screen dimensions for a landscape 4.3-inch display
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
FPS = 30

# Colors
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)
CRIMSON = (220, 20, 60)
FIREBRICK = (178, 34, 34)
ORANGE = (255, 165, 0)
DARK_ORANGE = (255, 140, 0)
CORAL = (255, 127, 80)
TOMATO = (255, 99, 71)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
LIGHT_YELLOW = (255, 255, 224)
LEMON_CHIFFON = (255, 250, 205)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
FOREST_GREEN = (34, 139, 34)
LIME_GREEN = (50, 205, 50)
LIGHT_GREEN = (144, 238, 144)
PALE_GREEN = (152, 251, 152)
SPRING_GREEN = (0, 255, 127)
CYAN = (0, 255, 255)
AQUA = (0, 255, 255)
TURQUOISE = (64, 224, 208)
TEAL = (0, 128, 128)
BLUE = (0, 150, 255)
DARK_BLUE = (0, 0, 139)
NAVY = (0, 0, 128)
MEDIUM_BLUE = (0, 0, 205)
ROYAL_BLUE = (65, 105, 225)
LIGHT_BLUE = (173, 216, 230)
SKY_BLUE = (135, 206, 235)
DEEP_SKY_BLUE = (0, 191, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 255)
VIOLET = (238, 130, 238)
ORCHID = (218, 112, 214)
LAVENDER = (230, 230, 250)
PINK = (255, 192, 203)
HOT_PINK = (255, 105, 180)
DARK_PURPLE = (75, 0, 130)
INDIGO = (75, 0, 130)
MAROON = (128, 0, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
SIENNA = (160, 82, 45)
SADDLE_BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (211, 211, 211)
SLATE_GRAY = (112, 128, 144)
DARK_GRAY = (169, 169, 169)
SILVER = (192, 192, 192)

# All Colors List
COLORS = [
    RED, DARK_RED, CRIMSON, FIREBRICK, ORANGE, DARK_ORANGE, 
    CORAL, TOMATO, YELLOW, GOLD, LIGHT_YELLOW, LEMON_CHIFFON, 
    GREEN, DARK_GREEN, FOREST_GREEN, LIME_GREEN, LIGHT_GREEN, 
    PALE_GREEN, SPRING_GREEN, CYAN, AQUA, TURQUOISE, TEAL, 
    BLUE, DARK_BLUE, NAVY, MEDIUM_BLUE, ROYAL_BLUE, LIGHT_BLUE, 
    SKY_BLUE, DEEP_SKY_BLUE, PURPLE, MAGENTA, VIOLET, ORCHID, 
    LAVENDER, PINK, HOT_PINK, DARK_PURPLE, INDIGO, MAROON, 
    BROWN, DARK_BROWN, SIENNA, SADDLE_BROWN, BLACK, WHITE, 
    GRAY, LIGHT_GRAY, SLATE_GRAY, DARK_GRAY, SILVER
]

# Fonts
font_xlarge = pygame.font.Font("./Fonts/digital-7.ttf", size=200)
font_large = pygame.font.Font("./Fonts/digital-7.ttf", size=120)
font_medlar = pygame.font.Font("./Fonts/digital-7.ttf", size=100)
font_medium = pygame.font.Font("./Fonts/digital-7.ttf", size=48)
font_small = pygame.font.Font("./Fonts/digital-7.ttf", size=36)

font_xlarge_clean = pygame.font.Font(size=200)
font_large_clean = pygame.font.Font(size=120)
font_medlar_clean = pygame.font.Font(size=100)
font_medium_clean = pygame.font.Font(size=48)
font_small_clean = pygame.font.Font(size=36)

# Path to the brightness file
brightness_file = "/sys/class/backlight/10-0045/brightness"

# Function to get current brightness
def get_brightness():
    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        return current_brightness
    except Exception as e:
        print(f"Error reading brightness: {e}")
        return 0

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
        return new_brightness
    except Exception as e:
        print(f"Error decreasing brightness: {e}")
        return 0

# Function to increase brightness
def increase_brightness():
    try:
        with open(brightness_file, "r") as file:
            current_brightness = int(file.read().strip())
        new_brightness = min(current_brightness + 15, 255)  # Adjust 20 to your desired increment
        adjust_brightness(new_brightness)
        return new_brightness
    except Exception as e:
        print(f"Error increasing brightness: {e}")
        return 0

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

# Function to draw text on screen with wrap around functionality
def draw_text(screen, text, font, color, x, y, max_width=None):
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

# Function to draw a rounded rectangle
def draw_rounded_rect(surface, color, rect, radius):
    # Draw the rounded corners using arcs
    x, y, width, height = rect
    pygame.draw.rect(surface, color, pygame.Rect(x + radius, y, width - 2 * radius, height))
    pygame.draw.rect(surface, color, pygame.Rect(x, y + radius, width, height - 2 * radius))
    
    pygame.draw.arc(surface, color, pygame.Rect(x, y, 2 * radius, 2 * radius), math.pi, 1.5 * math.pi, 0)
    pygame.draw.arc(surface, color, pygame.Rect(x + width - 2 * radius, y, 2 * radius, 2 * radius), 1.5 * math.pi, 2 * math.pi, 0)
    pygame.draw.arc(surface, color, pygame.Rect(x, y + height - 2 * radius, 2 * radius, 2 * radius), 0, 0.5 * math.pi, 0)
    pygame.draw.arc(surface, color, pygame.Rect(x + width - 2 * radius, y + height - 2 * radius, 2 * radius, 2 * radius), 0.5 * math.pi, math.pi, 0)

    # Fill the corners with the color
    corners = [(x + radius, y + radius),
               (x + width - radius, y + radius),
               (x + width - radius, y + height - radius),
               (x + radius, y + height - radius)]
    for corner in corners:
        pygame.draw.circle(surface, color, corner, radius)

# Function to display Chevrolet logo animation
def display_logo(screen):
    logo = pygame.image.load("Images/chevy.jpg").convert_alpha()
    logo_rect = logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Animation variables
    rotation_angle = 0
    scale = 0.6
    animation_duration = 1
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

        scale += 0.01

        pygame.time.Clock().tick(FPS)
    
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
