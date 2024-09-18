import pygame

# Initialize Pygame
pygame.init()

# Define screen dimensions and colors
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
RED = (255, 0, 0)
INDIGO = (75, 0, 130)
BACKGROUND_2_COLOR = (0, 255, 0)  # Example RGB color for BACKGROUND_2_COLOR

# Load the image you want to display in place of the background color
background_image = pygame.image.load("Images/chevy.jpg")  # Replace with your image path
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Create the main surface (the screen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Create a mask surface that will use the BACKGROUND_2_COLOR and become transparent
screen_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
screen_mask.fill(BACKGROUND_2_COLOR)

# Set the color key to make BACKGROUND_2_COLOR transparent on the mask
screen_mask.set_colorkey(BACKGROUND_2_COLOR)

# Boolean flag to control image inversion
invert_image = True  # Set this to True or False based on your needs

# Function to invert an image
def invert_image_colors(image):
    inverted_image = pygame.Surface(image.get_size())
    for x in range(image.get_width()):
        for y in range(image.get_height()):
            color = image.get_at((x, y))
            # Invert the color
            inverted_color = pygame.Color(255 - color.r, 255 - color.g, 255 - color.b, color.a)
            inverted_image.set_at((x, y), inverted_color)
    return inverted_image

# Function to tint an image
def tint_image(image, tint_color, invert=False):
    # Optionally invert the image first
    if invert:
        image = invert_image_colors(image)
    
    # Create a copy of the image to avoid modifying the original
    tinted_image = image.copy()
    # Apply the tint by filling it with the background color using BLEND_RGB_MULT
    tinted_image.fill(tint_color, special_flags=pygame.BLEND_RGB_MULT)
    return tinted_image

# In the main game loop or drawing function
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the main screen with a background color (for example, INDIGO)
    screen.fill(INDIGO)

    # Tint the background image with BACKGROUND_2_COLOR
    tinted_background = tint_image(background_image, BACKGROUND_2_COLOR, invert=invert_image)

    # Draw all your shapes, elements, etc., that use BACKGROUND_2_COLOR on the mask surface
    pygame.draw.rect(screen_mask, BACKGROUND_2_COLOR, (100, 100, 200, 200))  # Transparent area
    pygame.draw.rect(screen_mask, RED, (50, 50, 200, 100))  # This area will be opaque

    # Blit the tinted background image onto the screen first
    screen.blit(tinted_background, (0, 0))

    # Then blit the mask surface onto the screen (with transparency)
    screen.blit(screen_mask, (0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
