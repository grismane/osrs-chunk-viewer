import os
import pygame
from pygame._sdl2 import Window

# === Constants ===
# Map tiles
MAP_TILE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"
Z_MIN = 0
Z_MAX = 3
current_z = 0
INIT_CENTER = (49, 53)
INIT_LOAD_RADIUS = 8
INIT_LOAD_CORNER_START = (INIT_CENTER[0] - INIT_LOAD_RADIUS, INIT_CENTER[1] - INIT_LOAD_RADIUS)
INIT_LOAD_CORNER_END = (INIT_CENTER[0] + INIT_LOAD_RADIUS, INIT_CENTER[1] + INIT_LOAD_RADIUS)
TILE_SIZE = 256

# Zoom
ZOOM_LEVELS = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125]
ZOOM_SPEED = 0.02
zoom = zoom_target = 1.0

# Color constants for rendering
BACKGROUND_COLOUR = (0, 0, 0)
GRID_LINE_COLOUR = (255, 255, 255)

# Constants for overlay layout and appearance
PADDING_RIGHT = 32
PADDING_TOP = 32
LINE_SPACING = 8
OVERLAY_PADDING = 16
OVERLAY_BG_ALPHA = 128
FONT_SIZE = 48


def initialize_window():
    os.environ["SDL_AUDIODRIVER"] = "dummy" # set a dummy audio output to avoid error in pygame
    pygame.mixer.init()
    pygame.init()
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    info = pygame.display.Info() # Get screen dimensions
    window_width = info.current_w or 1280
    window_height = info.current_h or 720
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE) # Create the screen surface
    pygame.display.set_caption("OSRS Map Viewer") # Window title
    Window.from_display_module().maximize() # Maximize the window
    return screen, window_width, window_height

def init_load(map_tile_dir):
    loaded_tiles = {} # dictionary of loaded tile images
    for tile_image in os.listdir(map_tile_dir):
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)        
    pass

def slow_load():
    pass

def draw_tiles_and_grid():
    pass

def draw_overlay():
    pass

def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False # Stop the main loop
    return True

def main():
    loaded_tiles, x_min, x_max, y_min, y_max = init_load(MAP_TILE_DIR)
    global 

    screen, window_width, window_height = initialize_window()
    running = True

    while running:
        if not handle_events():
            break # Window was closed
        
        screen.fill(BACKGROUND_COLOUR) # Render solid background
        pygame.display.flip() # Update display
    
    pygame.quit()

# Run the main function if this script is executed
if __name__ == "__main__":
    main()