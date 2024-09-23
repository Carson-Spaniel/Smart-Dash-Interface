from .builder import *
from .brain import draw_text, draw_rounded_rect
from math import floor
import time

last_blink_time = time.time()  # Initialize at the current time
blink_on = True  # Initial state of the blink pattern

def update_blink_pattern():
    """
    Update the blink pattern based on elapsed time.

    Toggles the blink state (on/off) every 0.1 seconds.
    """

    global last_blink_time, blink_on

    current_time = time.time()
    elapsed_time = current_time - last_blink_time

    # Blink on for 0.1 seconds and off for 0.1 seconds
    if elapsed_time >= 0.1:  # Time to toggle
        blink_on = not blink_on  # Toggle the blink state (on/off)
        last_blink_time = current_time  # Reset the last blink time

def page_guide(screen, screen_2, FONT_COLOR, BACKGROUND_2_COLOR, pages, current_page):
    """
    Draw the page indicators at the bottom of the screen.

    Parameters:
        screen: The main screen to draw on.
        screen_2: A secondary screen to draw on.
        FONT_COLOR: Color for the text.
        BACKGROUND_2_COLOR: Background color for the page indicators.
        pages: List of pages to indicate.
        current_page: Tuple indicating the current page indices.
    """
    
    # Clear the screen
    screen.fill(BACKGROUND_2_COLOR)
    screen_2.fill(BACKGROUND_2_COLOR)

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
        color = FONT_COLOR if i == current_page[0] else BACKGROUND_2_COLOR
        pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius + 4)
        pygame.draw.circle(screen, BACKGROUND_2_COLOR, (circle_x, circle_y), circle_radius + 2)
        pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
        circle_x += 2 * (circle_radius + circle_spacing)

    # Calculate total height occupied by circles
    total_circle_height = (len(pages[0])) * (2 * circle_radius + circle_spacing) + circle_spacing + (2 * circle_radius)

    # Calculate starting position to center vertically
    start_y = (SCREEN_HEIGHT - total_circle_height) // 2
    circle_x = SCREEN_WIDTH - circle_radius - circle_spacing
    circle_y = start_y + circle_radius + circle_spacing

    for i, page in enumerate(pages[current_page[0]]):
        color = FONT_COLOR if i == current_page[1] else BACKGROUND_2_COLOR
        pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius + 4)
        pygame.draw.circle(screen, BACKGROUND_2_COLOR, (circle_x, circle_y), circle_radius + 2)
        pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
        circle_y += 2 * (circle_radius + circle_spacing)

def rpm_page(screen, FONT_COLOR, DEV, supported, rpm, rpm_max, shift, connect):
    """
    Draw the RPM settings page with various indicators.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        DEV: Boolean indicating if development mode is active.
        supported: List of supported features.
        rpm: Current RPM value.
        rpm_max: Maximum RPM value.
        shift: Shift value.
        connect: Boolean indicating connection status.
    """
    
    draw_text(screen, "RPM Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

    if DEV or '0x0C' in supported:
        # Draw RPM section
        draw_text(screen, "RPM", font_medium_clean, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
        draw_text(screen, str(rpm), font_large, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)
        draw_text(screen, "Max", font_small_clean, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2)
        draw_text(screen, str(rpm_max), font_medium, FONT_COLOR, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2 +40)
        draw_text(screen, "Shift", font_small_clean, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2)
        draw_text(screen, str(shift), font_medium, FONT_COLOR, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2 +40)

        # Draw buttons for increasing and decreasing RPM
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

        draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
        draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)

        # Draw another set of buttons for increasing and decreasing shift
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

        draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
        draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
    
    else:
        # Display connection status if RPM is not supported
        if not connect:
            draw_text(screen, "Not connected to car", font_medium_clean, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)
        else:
            draw_text(screen, "RPM is not supported by car", font_medium_clean, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)

def main_page(screen, FONT_COLOR, BACKGROUND_1_COLOR, BACKGROUND_2_COLOR, fuel_level, rpm, rpm_max, shift, optimize, shift_light, mpg, speed, air_temp, voltage, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding):
    """
    Draw the main dashboard page displaying various vehicle metrics.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        BACKGROUND_1_COLOR: Background color for the main section.
        BACKGROUND_2_COLOR: Background color for overlays.
        fuel_level: Current fuel level as a percentage.
        rpm: Current RPM value.
        rpm_max: Maximum RPM value.
        shift: Shift threshold for the vehicle.
        optimize: Boolean to indicate if optimization mode is active.
        shift_light: Boolean to indicate if shift lights should be displayed.
        mpg: Current miles per gallon.
        speed: Current speed in miles per hour.
        air_temp: Current air temperature in Celsius.
        voltage: Current voltage level.
        shift_color_1, shift_color_2, shift_color_3, shift_color_4: Colors for shift indicators.
        shift_padding: Padding for shift lights coming on.
    """

    screen.fill(BACKGROUND_1_COLOR)

    # Calculate the width of the filled portion based on percentage
    fuel_width = floor((SCREEN_WIDTH*.7663) * fuel_level/100)

    # Determine fuel color based on the fuel level
    if fuel_level > 75:
        fuel_color = GREEN
    elif fuel_level <=75 and fuel_level > 50:
        fuel_color = YELLOW
    elif fuel_level <=50 and fuel_level > 30:
        fuel_color = ORANGE
    else:
        fuel_color = RED
    
    pygame.draw.rect(screen, fuel_color, (SCREEN_WIDTH*.22, SCREEN_HEIGHT*.75, fuel_width, SCREEN_HEIGHT*.22))

    # Calculate the percentage of RPM relative to rpm_max
    rpm_percentage = min(1.0, rpm / rpm_max)  # Ensure it's between 0 and 1
    
    # Calculate the height of the filled portion based on percentage
    rpm_width = floor((SCREEN_WIDTH*.98) * rpm_percentage)

    # Draw the filled portion
    rpm_color = GREEN if rpm<shift else RED

    # Draw the shift line
    shiftLineColor = RED if rpm<shift else BLACK
    shift_line_x = SCREEN_WIDTH - (shift / rpm_max) * SCREEN_WIDTH*.99

    # Draw the RPM bar and shift line
    pygame.draw.rect(screen, rpm_color, (SCREEN_WIDTH * 0.01, 0, rpm_width, SCREEN_HEIGHT*.25))
    pygame.draw.line(screen, shiftLineColor, (SCREEN_WIDTH-shift_line_x, 0), (SCREEN_WIDTH-shift_line_x, SCREEN_HEIGHT*.25), 5)

    # Draw rounded rectangles for overlay effects
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),  20, 120)
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT*.03))
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, pygame.Rect(0, SCREEN_HEIGHT-SCREEN_HEIGHT*.03, SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, pygame.Rect(SCREEN_WIDTH-SCREEN_WIDTH*.02, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, pygame.Rect(0, 0, SCREEN_WIDTH*.02, SCREEN_HEIGHT))

    # Draw circular overlays in corners
    pygame.draw.circle(screen, BACKGROUND_2_COLOR, (0, 0), SCREEN_WIDTH*.085)
    # pygame.draw.circle(screen, BACKGROUND_2_COLOR, (0, SCREEN_HEIGHT), SCREEN_WIDTH*.085)
    pygame.draw.circle(screen, BACKGROUND_2_COLOR, (SCREEN_WIDTH, 0), SCREEN_WIDTH*.085)
    pygame.draw.circle(screen, BACKGROUND_2_COLOR, (SCREEN_WIDTH, SCREEN_HEIGHT), SCREEN_WIDTH*.085)

    # Draw the main content area with rounded corners
    draw_rounded_rect(screen, BACKGROUND_2_COLOR, (SCREEN_WIDTH//2-((SCREEN_WIDTH*.89)//2), SCREEN_HEIGHT//2-((SCREEN_HEIGHT*.83)//2), SCREEN_WIDTH*.89, SCREEN_HEIGHT*.83), 90)

    # Draw additional rectangles for aesthetic separation
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, pygame.Rect(SCREEN_WIDTH//2-((SCREEN_WIDTH*.89)//2), SCREEN_HEIGHT//2-((SCREEN_HEIGHT*.83)//2), SCREEN_WIDTH*.89, SCREEN_HEIGHT*.83),  20, 90)
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, (0, SCREEN_HEIGHT*.25, SCREEN_WIDTH * .22, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, (SCREEN_WIDTH-SCREEN_WIDTH*.22, SCREEN_HEIGHT*.25, SCREEN_WIDTH, SCREEN_HEIGHT*.5))
    pygame.draw.rect(screen, BACKGROUND_2_COLOR, (SCREEN_WIDTH*.12, SCREEN_HEIGHT*.15, SCREEN_WIDTH*.75, SCREEN_HEIGHT*.7))
    
    # Draw fuel level percentage text
    draw_text(screen, f"{round(fuel_level,1)}%", font_medium, FONT_COLOR, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.93)

    # Draw RPM display
    draw_text(screen, f"{rpm}", font_xlarge, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT//2)
    draw_text(screen, "RPM", font_small_clean, FONT_COLOR, SCREEN_WIDTH // 2, SCREEN_HEIGHT*.7)

    # Draw additional metrics if not in optimization mode
    if not optimize:
        draw_text(screen,f"{(round(mpg, 2))}", font_medlar, FONT_COLOR, SCREEN_WIDTH *.13, SCREEN_HEIGHT // 2)
        draw_text(screen, "MPG", font_small_clean, FONT_COLOR, SCREEN_WIDTH *.13, SCREEN_HEIGHT // 2+50)

        draw_text(screen, f"{int(round(speed,0))}", font_medlar, FONT_COLOR, SCREEN_WIDTH *.87, SCREEN_HEIGHT // 2)
        draw_text(screen, "MPH", font_small_clean, FONT_COLOR, SCREEN_WIDTH *.87, SCREEN_HEIGHT // 2+50)

        draw_text(screen, f"{round((air_temp*(9/5))+32,1)}F", font_medium, FONT_COLOR, SCREEN_WIDTH*.7, SCREEN_HEIGHT - SCREEN_HEIGHT*.15)
        draw_text(screen, f"{round(voltage,1)} v", font_medium, FONT_COLOR, SCREEN_WIDTH*.3, SCREEN_HEIGHT - SCREEN_HEIGHT*.15)

    # Draw shift lights if enabled
    if shift_light:
        circle_radius = 24
        circle_spacing = 4

        # Calculate total width for shift lights
        total_circle_width = 12 * (2 * circle_radius + 2 * circle_spacing)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = circle_radius + circle_spacing + SCREEN_HEIGHT * .17

        # Colors for each light
        light_colors = [COLORS[shift_color_1], COLORS[shift_color_1], COLORS[shift_color_1], COLORS[shift_color_1],
                        COLORS[shift_color_2], COLORS[shift_color_2], COLORS[shift_color_2], COLORS[shift_color_2],
                        COLORS[shift_color_3], COLORS[shift_color_3], COLORS[shift_color_3], COLORS[shift_color_3]]

        update_blink_pattern()  # Update the blink pattern based on the time

        # Draw each shift light
        for i in range(len(light_colors)):
            color = light_colors[i]

            pygame.draw.circle(screen, FONT_COLOR, (circle_x, circle_y), circle_radius)
            pygame.draw.circle(screen, BACKGROUND_2_COLOR, (circle_x, circle_y), circle_radius - 3)

            # Logic for blinking shift lights based on RPM
            if rpm > shift:
                if blink_on:
                    pygame.draw.circle(screen, COLORS[shift_color_4], (circle_x, circle_y), circle_radius)
                else:
                    pygame.draw.circle(screen, BACKGROUND_2_COLOR, (circle_x, circle_y), circle_radius)

            if rpm > shift - (((len(light_colors) + 2) - i) * shift_padding):
                if rpm > shift:
                    if blink_on:
                        pygame.draw.circle(screen, COLORS[shift_color_4], (circle_x, circle_y), circle_radius)
                    else:
                        pygame.draw.circle(screen, BACKGROUND_2_COLOR, (circle_x, circle_y), circle_radius)
                elif rpm < shift and rpm > shift - 200:
                    pygame.draw.circle(screen, COLORS[shift_color_4], (circle_x, circle_y), circle_radius)
                else:
                    pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)

            circle_x += 2 * (circle_radius + circle_spacing)

def settings_page(screen, FONT_COLOR, brightness, optimize, delay):
    """
    Draws the settings page, allowing users to adjust brightness, optimization mode, and reading delay.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        brightness: Current brightness level (0-255).
        optimize: Boolean indicating if optimization mode is enabled.
        delay: Boolean indicating if reading delay is enabled.
    """
    
    draw_text(screen, "General Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

    # Button to flip settings
    pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH // 2 - SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "FLIP", font_small_clean, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)

    # Brightness adjustment buttons
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.50, SCREEN_HEIGHT*.20, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.70, SCREEN_HEIGHT*.20, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

    draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.25)
    draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.25)
    draw_text(screen, f"{int(round((brightness/255)*100,0))}%", font_small, FONT_COLOR, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
    draw_text(screen, "Brightness", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

    # Optimization toggle
    pygame.draw.rect(screen, GREEN if optimize else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.32, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "On" if optimize else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
    draw_text(screen, "Optimize readings", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

    # Delay toggle
    pygame.draw.rect(screen, GREEN if delay else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.44, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "On" if delay else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)
    draw_text(screen, "Delay readings", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)

def trouble_page(screen, FONT_COLOR, codes, cleared):
    """
    Displays trouble codes and allows the user to clear them.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        codes: List of trouble codes (tuples of (code, description)).
        cleared: Boolean indicating if codes are currently being cleared.
    """

    draw_text(screen, "Trouble Codes", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)
                
    if len(codes):
        if cleared:
            if cleared == 2:
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
        draw_text(screen, f"{'Trouble codes have been cleared, Please restart car' if cleared else 'No trouble codes detected'}", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.25)

def info_page(screen, FONT_COLOR, SYSTEM_VERSION, wifi, development_mode):
    """
    Displays system information including version and connectivity status.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        SYSTEM_VERSION: Current system version.
        wifi: Boolean indicating if there is a Wi-Fi connection.
        development_mode: Boolean indicating if development mode is enabled.
    """

    draw_text(screen, "System Information", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)
    draw_text(screen, f"Version: {SYSTEM_VERSION}", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.15)

    # Exit button
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH//2 - SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "Exit", font_small_clean, BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT-SCREEN_HEIGHT*.15)

    # Wi-Fi status
    pygame.draw.rect(screen, GREEN if wifi else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.05, SCREEN_HEIGHT*.2, SCREEN_WIDTH*.2, SCREEN_HEIGHT*.1))
    draw_text(screen, "Update" if wifi else "No Wifi", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
    draw_text(screen, "Update System", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

    # Development mode toggle
    pygame.draw.rect(screen, GREEN if development_mode else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.32, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "On" if development_mode else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
    draw_text(screen, "Development Mode", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

def custom_page(screen, FONT_COLOR, font_index, background_1_index, background_2_index, images, image_index):
    """
    Allows users to customize font and background settings.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        font_index: Index for the selected font color.
        background_1_index: Index for the first background color.
        background_2_index: Index for the second background color.
        images: List of available background images.
        image_index: Index for the selected background image.
    """
    
    draw_text(screen, "Customization Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

    # Font color selection
    pygame.draw.rect(screen, COLORS[font_index], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.2, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.25)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.25)
    draw_text(screen, f"{font_index+1}", font_small, BLACK if COLORS[font_index] != BLACK else WHITE, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
    draw_text(screen, "Font Color", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

    # Background color 1 selection
    pygame.draw.rect(screen, COLORS[background_1_index], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.32, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.37)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.37)
    draw_text(screen, f"{background_1_index+1}", font_small, BLACK if COLORS[background_1_index] != BLACK else WHITE, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
    draw_text(screen, "Background Color 1", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

    # Background color 2 selection
    pygame.draw.rect(screen, COLORS[background_2_index], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.44, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.49)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.49)
    draw_text(screen, f"{background_2_index+1}", font_small, FONT_COLOR, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)
    draw_text(screen, "Background Color 2", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)

    # Display selected background image
    new_image = pygame.image.load(images[image_index])
    new_image = pygame.transform.scale(new_image, (SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    screen.blit(new_image, (((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1), SCREEN_HEIGHT*.56))

    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.61)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.61)
    draw_text(screen, f"{image_index+1}", font_small, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.61)
    draw_text(screen, "Background Image", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.61)

def color_1_page(screen, FONT_COLOR, shift, shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding):
    """
    Adjusts settings for shift lights and their colors.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        shift: Current shift value.
        shift_light: Boolean indicating if shift lights are enabled.
        shift_color_1: Index for the first shift light color.
        shift_color_2: Index for the second shift light color.
        shift_color_3: Index for the third shift light color.
        shift_color_4: Index for the fourth shift light color.
        shift_padding: Padding value affecting the shift RPM calculation.
    """

    draw_text(screen, "Shift Light Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

    # Shift light toggle
    pygame.draw.rect(screen, GREEN if shift_light else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "On" if shift_light else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
    draw_text(screen, "Shift lights", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

    # Color selection for shift light 1
    pygame.draw.rect(screen, COLORS[shift_color_1], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.32, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.37)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.37)
    draw_text(screen, f"{shift_color_1+1}", font_small, BLACK if COLORS[shift_color_1] != BLACK else WHITE, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
    draw_text(screen, "Shift Light Color 1", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

    # Color selection for shift light 2
    pygame.draw.rect(screen, COLORS[shift_color_2], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.44, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.49)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.49)
    draw_text(screen, f"{shift_color_2+1}", font_small, BLACK if COLORS[shift_color_2] != BLACK else WHITE, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)
    draw_text(screen, "Shift Light Color 2", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.49)

    # Color selection for shift light 3
    pygame.draw.rect(screen, COLORS[shift_color_3], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.56, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.61)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.61)
    draw_text(screen, f"{shift_color_3+1}", font_small, BLACK if COLORS[shift_color_3] != BLACK else WHITE, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.61)
    draw_text(screen, "Shift Light Color 3", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.61)

    # Color selection for shift light 4
    pygame.draw.rect(screen, COLORS[shift_color_4], ((SCREEN_WIDTH//2)+SCREEN_WIDTH*.1, SCREEN_HEIGHT*.68, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "<", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.73)
    draw_text(screen, ">", font_medium, FONT_COLOR, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.73)
    draw_text(screen, f"{shift_color_4+1}", font_small, BLACK if COLORS[shift_color_4] != BLACK else WHITE, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.73)
    draw_text(screen, "Shift Light Color 4", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.73)

    # Adjust shift starting RPM
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.50, SCREEN_HEIGHT*.80, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.70, SCREEN_HEIGHT*.80, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

    draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.55, SCREEN_HEIGHT*.85)
    draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.75, SCREEN_HEIGHT*.85)
    draw_text(screen, f"{shift - (14 * shift_padding)}", font_small, FONT_COLOR, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.85)
    draw_text(screen, "Shift Starting RPM", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.85)

def developmental_page(screen, FONT_COLOR, show_fps, experimental, query_times):
    """
    Displays development settings, allowing the user to toggle FPS display.

    Parameters:
        screen: The screen to draw on.
        FONT_COLOR: Color for the text.
        show_fps: Boolean indicating if FPS display is enabled.
        experimental: Boolean indicating if experimental mode is enabled.
        query_times: Dictionary of query times.
    """
        
    draw_text(screen, "Development Settings", font_small_clean, FONT_COLOR, SCREEN_WIDTH//2, SCREEN_HEIGHT*.05)

    # Toggle FPS display
    pygame.draw.rect(screen, GREEN if show_fps else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.2, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "On" if show_fps else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)
    draw_text(screen, "Frames Per Second", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.25)

    # Toggle experimental settings
    pygame.draw.rect(screen, GREEN if experimental else RED, (SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1, SCREEN_HEIGHT*.32, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.1))
    draw_text(screen, "On" if experimental else "Off", font_small_clean, BLACK, (SCREEN_WIDTH//2)+SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)
    draw_text(screen, "Experimental Mode", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2)-SCREEN_WIDTH*.15, SCREEN_HEIGHT*.37)

    if experimental:
        # Show experimental queries
        draw_text(screen, f"Queries: {query_times}", font_small_clean, FONT_COLOR, (SCREEN_WIDTH//2), SCREEN_HEIGHT*.49, SCREEN_WIDTH*.5)