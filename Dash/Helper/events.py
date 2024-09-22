from .builder import *
from .brain import increase_brightness, decrease_brightness, save_rpm

def swipe_event(mouse_button_down, event, swipe_start_x, swipe_start_y, swipe_threshold, current_page, pages):
    """
    Handle swipe events to navigate between pages.

    Parameters:
        mouse_button_down (bool): Indicates if the mouse button is pressed.
        event: The event object containing mouse position.
        swipe_start_x (int): Initial X position of the swipe.
        swipe_start_y (int): Initial Y position of the swipe.
        swipe_threshold (int): Minimum distance to register a swipe.
        current_page (tuple): Current page index and sub-index.
        pages (list): List of available pages.

    Returns:
        tuple: Updated current page and mouse button state.
    """

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

    return current_page, mouse_button_down

def rpm_event(mouseX, mouseY, rpm_max, shift):
    """
    Handle RPM adjustment based on mouse clicks.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        rpm_max (int): Current maximum RPM value.
        shift (int): Current shift value.

    Returns:
        tuple: Updated rpm_max and shift values.
    """

    # Check for collision with increase rectangle
    if mouseX < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.2+25 and mouseY < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.3:
        rpm_max += 100  # Increase rpm_max by 100

        if rpm_max > 50000:
            rpm_max = 50000

        # Save the new max horsepower data
        save_rpm(rpm_max,shift)

    # Check for collision with decrease rectangle
    elif mouseX < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.2+25 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
        rpm_max -= 100  # Decrease rpm_max by 100
        if rpm_max == 0:
            rpm_max = 100

        if shift > rpm_max:
            shift = rpm_max

        # Save the new max horsepower data
        save_rpm(rpm_max,shift)

    # Check for collision with increase rectangle
    elif mouseX < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7-25 and mouseY < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.3:
        shift += 100  # Increase shift by 100

        if shift > rpm_max:
            shift = rpm_max

        # Save the new max horsepower data
        save_rpm(rpm_max,shift)

    # Check for collision with decrease rectangle
    elif mouseX < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7-25 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
        shift -= 100  # Decrease shift by 100

        if shift == 0:
            shift = 100

        # Save the new max horsepower data
        save_rpm(rpm_max,shift)

    return rpm_max, shift

def settings_event(mouseX, mouseY, brightness, optimize, FLIP, delay, holding = False):
    """
    Handle settings adjustments based on mouse clicks.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        brightness (int): Current brightness level.
        optimize (bool): Current optimization setting.
        FLIP (bool): Current flip setting.
        delay (bool): Current delay setting.
        holding (bool): Indicates if the mouse button is held down.

    Returns:
        tuple: Updated brightness, optimize, FLIP, and delay values.
    """

    # Check for collision with decrease rectangle
    if mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
        brightness = decrease_brightness()                            
    
    # Check for collision with increase rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
        brightness = increase_brightness()

    if not holding:
        # Check for collision with optimize rectangle
        if mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.42 and mouseY > SCREEN_HEIGHT*.32:
            if optimize:
                optimize = False
            else:
                optimize = True

        # Check for collision with flip rectangle
        elif mouseX < SCREEN_WIDTH//2 + SCREEN_WIDTH*.05 and mouseX > SCREEN_WIDTH//2 - SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
            if FLIP:
                FLIP = False
            else:
                FLIP = True

        # Check for collision with delay rectangle
        elif mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.54 and mouseY > SCREEN_HEIGHT*.44:
            if delay:
                delay = False
            else:
                delay = True

    return brightness, optimize, FLIP, delay

def trouble_event(mouseX, mouseY, clear):
    """
    Handle trouble event to clear status.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        clear (bool): Indicates if the status is already cleared.

    Returns:
        bool: Updated clear status.
    """

    # Check for collision with exit rectangle
    if not clear: # To prevent multiple clears
        if mouseX < SCREEN_WIDTH//2 + SCREEN_WIDTH*.06 and mouseX > SCREEN_WIDTH//2 - SCREEN_WIDTH*.06 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
            clear = True

    return clear

def info_event(mouseX, mouseY, wifi, logging, exit_text, development_mode):
    """
    Handle information events based on mouse clicks.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        wifi (bool): Indicates Wi-Fi status.
        logging (bool): Indicates logging status.
        exit_text (str): Text to display when exiting.
        development_mode (bool): Indicates development mode status.

    Returns:
        tuple: Updated logging status, exit text, and development mode status.
    """
    
    # Check for collision with exit rectangle
    if mouseX < SCREEN_WIDTH//2 + SCREEN_WIDTH*.05 and mouseX > SCREEN_WIDTH//2 - SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT-SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT-SCREEN_HEIGHT*.2:
        logging = False
        exit_text = "Exiting..."
    
    # Check for collision with update rectangle
    elif mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.25 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.05 and mouseY < SCREEN_HEIGHT*.3 and mouseY > SCREEN_HEIGHT*.2:
        if wifi:
            logging = False
            exit_text = "Update System"

    # Check for collision with update rectangle
    elif mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.42 and mouseY > SCREEN_HEIGHT*.32:
        if development_mode:
            development_mode = False
        else:
            development_mode = True

    return logging, exit_text, development_mode

def development_event(mouseX, mouseY, show_fps):
    """
    Handle developmental feature toggling based on mouse clicks.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        show_fps (bool): Indicates if FPS should be displayed.

    Returns:
        bool: Updated show_fps status.
    """

    # Check for collision with optimize rectangle
    if mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.3 and mouseY > SCREEN_HEIGHT*.2:
        if show_fps:
            show_fps = False
        else:
            show_fps = True

    return show_fps

def custom_event(mouseX, mouseY, images, font_index, background_1_index, background_2_index, image_index, changed_image, holding = False):
    """
    Handle custom image and font settings based on mouse clicks.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        images (list): List of available images.
        font_index (int): Current font index.
        background_1_index (int): Current index for background 1.
        background_2_index (int): Current index for background 2.
        image_index (int): Current image index.
        changed_image (bool): Indicates if the image has changed.
        holding (bool): Indicates if the mouse button is held down.

    Returns:
        tuple: Updated font index, background indices, image index, and changed image status.
    """

    # Check for collision with left rectangle
    if mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
        font_index = (font_index - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
        font_index = (font_index + 1) % len(COLORS)

    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.32+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.32:
        background_1_index = (background_1_index - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.32+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.32:
        background_1_index = (background_1_index + 1) % len(COLORS)

    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.44+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.44:
        background_2_index = (background_2_index - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.44+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.44:
        background_2_index = (background_2_index + 1) % len(COLORS)

    if not holding:
        # Check for collision with left rectangle
        if mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.56+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.56:
            image_index = (image_index - 1) % len(images)
            changed_image = True

        # Check for collision with right rectangle
        elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.56+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.56:
            image_index = (image_index + 1) % len(images)
            changed_image = True

    return font_index, background_1_index, background_2_index, image_index, changed_image

def color_1_event(mouseX, mouseY, shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding):
    """
    Handle color adjustments based on mouse clicks.

    Parameters:
        mouseX (int): X position of the mouse.
        mouseY (int): Y position of the mouse.
        shift_light (bool): Indicates if the shift light is on.
        shift_color_1 (int): Current index for color 1.
        shift_color_2 (int): Current index for color 2.
        shift_color_3 (int): Current index for color 3.
        shift_color_4 (int): Current index for color 4.
        shift_padding (int): Current padding value.

    Returns:
        tuple: Updated shift light, color indices, and padding value.
    """
        
    # Check for collision with shift light rectangle
    if mouseX < SCREEN_WIDTH // 2 + SCREEN_WIDTH*.2 and mouseX > SCREEN_WIDTH // 2 + SCREEN_WIDTH*.1 and mouseY < SCREEN_HEIGHT*.2+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.2:
        if shift_light:
            shift_light = False
        else:
            shift_light = True
    
    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.32+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.32:
        shift_color_1 = (shift_color_1 - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.32+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.32:
        shift_color_1 = (shift_color_1 + 1) % len(COLORS)

    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.44+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.32:
        shift_color_2 = (shift_color_2 - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.44+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.44:
        shift_color_2 = (shift_color_2 + 1) % len(COLORS)

    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.56+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.56:
        shift_color_3 = (shift_color_3 - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.56+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.56:
        shift_color_3 = (shift_color_3 + 1) % len(COLORS)

    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.68+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.68:
        shift_color_4 = (shift_color_4 - 1) % len(COLORS)

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.68+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.68:
        shift_color_4 = (shift_color_4 + 1) % len(COLORS)

    # Check for collision with left rectangle
    elif mouseX < SCREEN_WIDTH * 0.5 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.5 and mouseY < SCREEN_HEIGHT*.8+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.8:
        shift_padding += 10

        if shift_padding >= 210:
            shift_padding = 200

    # Check for collision with right rectangle
    elif mouseX < SCREEN_WIDTH * 0.7 + SCREEN_WIDTH*.1 and mouseX > SCREEN_WIDTH * 0.7 and mouseY < SCREEN_HEIGHT*.8+SCREEN_HEIGHT*.1 and mouseY > SCREEN_HEIGHT*.8:
        shift_padding -= 10

        if shift_padding <= 0:
            shift_padding = 10

    return shift_light, shift_color_1, shift_color_2, shift_color_3, shift_color_4, shift_padding