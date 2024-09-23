import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions for a landscape 4.3-inch display
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480

# Frames rendered per second
FPS = 45

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
DARK = (60, 60, 60)

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
    GRAY, LIGHT_GRAY, SLATE_GRAY, DARK_GRAY, SILVER, DARK
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