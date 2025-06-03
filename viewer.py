import os
# Set SDL audio driver to "dummy" to avoid audio issues when running the program
os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame
from pygame._sdl2 import Window
import re

# === Constants ===
TILE_SIZE = 256
BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"
ZOOM_LEVELS = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125]
ZOOM_SPEED = 0.02
START_CENTER_TILE = (49, 53)

# Color constants for rendering
WHITE = (255, 255, 255)
WHITE_50 = (255, 255, 255, 128)

# Constants for overlay layout and appearance
PADDING_RIGHT = 32
PADDING_TOP = 32
LINE_SPACING = 8
OVERLAY_PADDING = 16
OVERLAY_BG_ALPHA = 128
FONT_SIZE = 48


# Function to load map tiles from disk
def load_tiles(base_dir, stage):
    # Dictionary to store the loaded tiles
    tile_images = {}
    # Variables to track the map's min and max x/y coordinates
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    # Regular expression to match the filenames of the tiles (expected format: "z_x_y.png")
    pattern = re.compile(r"(\d+)_(\d+)_(\d+)")

    # Loop through the 4 possible zoom levels (0 to 3)
    for z in range(4):
        # Handle the different loading stages
        if stage == 1 and z != 0:
            continue
        if stage == 2 and z == 0:
            continue

        # Directory for the current zoom level
        z_dir = os.path.join(base_dir, str(z))
        if not os.path.isdir(z_dir):
            continue

        # Iterate through all files in the zoom level directory
        for filename in os.listdir(z_dir):
            # Only process PNG files
            if not filename.lower().endswith(".png"):
                continue
            # Match the tile filename with the expected pattern (z_x_y.png)
            match = pattern.match(filename)
            if not match:
                continue

            # Extract the zoom level (z), x-coordinate, and y-coordinate from the filename
            z_str, x_str, y_str = match.groups()
            x, y = int(x_str), int(y_str)

            try:
                # Try to load the image file
                img_path = os.path.join(z_dir, filename)
                print(f"Loading tile: {filename}")
                surface = pygame.image.load(img_path)
                if surface.get_alpha() is not None:
                    image = surface.convert_alpha()  # If the image has transparency, use convert_alpha
                else:
                    image = surface.convert()  # Otherwise, just convert the image to a surface
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                # If there's an error loading the tile, create a black placeholder tile
                image = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert()
                image.fill((0, 0, 0))  # Fill the tile with black color

            if not isinstance(image, pygame.Surface):
                continue  # Skip if the image isn't a valid pygame surface

            # Store the loaded tile in the tile_images dictionary with (z, x, y) as the key
            tile_images[(z, x, y)] = image
            # Update the min/max coordinates based on the tile's position
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

    if not tile_images:
        print("No tiles loaded.")
        return {}, 0, 0, 0, 0

    print(f"Loaded {len(tile_images)} tiles.")
    return tile_images, min_x, max_x, min_y, max_y


# Function to handle user input events (mouse, keyboard, etc.)
def handle_events():
    global dragging, drag_start, offset, zoom_target, current_z
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # If the user closes the window, exit the program
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Start dragging when the left mouse button is pressed
            dragging = True
            drag_start = event.pos
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Change cursor to a hand
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Stop dragging when the left mouse button is released
            dragging = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Restore cursor to default
        elif event.type == pygame.MOUSEMOTION and dragging:
            # Update the offset based on the mouse movement during dragging
            dx = event.pos[0] - drag_start[0]
            dy = event.pos[1] - drag_start[1]
            offset[0] += dx
            offset[1] += dy
            drag_start = event.pos
        elif event.type == pygame.KEYDOWN:
            # Change zoom level based on up/down arrow keys
            if event.key == pygame.K_UP and current_z < MAX_Z:
                current_z += 1
            elif event.key == pygame.K_DOWN and current_z > MIN_Z:
                current_z -= 1
        elif event.type == pygame.MOUSEWHEEL:
            # Change zoom level based on mouse wheel scroll
            try:
                idx = ZOOM_LEVELS.index(zoom)
            except ValueError:
                closest = min(ZOOM_LEVELS, key=lambda z: abs(z - zoom))
                idx = ZOOM_LEVELS.index(closest)

            if event.y > 0 and idx > 0:
                zoom_target = ZOOM_LEVELS[idx - 1]
            elif event.y < 0 and idx < len(ZOOM_LEVELS) - 1:
                zoom_target = ZOOM_LEVELS[idx + 1]
    return True


# Function to render the map tiles and grid on the screen
def draw_tiles_and_grid():
    for (z, x, y), image in tile_images.items():
        if not isinstance(image, pygame.Surface):
            continue  # Skip if the image isn't a valid surface
        if z != current_z:
            continue  # Only draw tiles for the current zoom level (current_z)
        
        tile_size_zoomed = TILE_SIZE * zoom  # Adjust tile size based on zoom level
        # Calculate the screen coordinates for this tile
        draw_x = (x - min_x) * tile_size_zoomed + offset[0]
        draw_y = (max_y - y) * tile_size_zoomed + offset[1]

        # Only draw tiles that are within the visible screen area
        if -tile_size_zoomed < draw_x < WINDOW_WIDTH and -tile_size_zoomed < draw_y < WINDOW_HEIGHT:
            # Scale the tile according to the zoom level
            scaled = pygame.transform.smoothscale(image, (int(tile_size_zoomed), int(tile_size_zoomed)))
            screen.blit(scaled, (draw_x, draw_y))

            # Draw a grid over the tiles
            rect = pygame.Rect(draw_x, draw_y, tile_size_zoomed, tile_size_zoomed)
            if x % 2 == 0:
                pygame.draw.line(screen, WHITE, rect.topleft, rect.bottomleft, 1)
                edge = pygame.Surface((1, rect.height), pygame.SRCALPHA)
                edge.fill(WHITE_50)
                screen.blit(edge, (rect.right - 1, rect.top))
            else:
                pygame.draw.line(screen, WHITE, rect.topright, rect.bottomright, 1)
            if y % 2 == 1:
                pygame.draw.line(screen, WHITE, rect.topleft, rect.topright, 1)
                edge = pygame.Surface((rect.width, 1), pygame.SRCALPHA)
                edge.fill(WHITE_50)
                screen.blit(edge, (rect.left, rect.bottom - 1))
            else:
                pygame.draw.line(screen, WHITE, rect.bottomleft, rect.bottomright, 1)


# Function to render the overlay (e.g., showing zoom level and map bounds)
def draw_overlay():
    font = pygame.font.SysFont(None, FONT_SIZE)
    # Display the current zoom level and floor (layer)
    text = f"Floor: {current_z}    Zoom: {int(zoom * 100)}%"
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(topright=(WINDOW_WIDTH - PADDING_RIGHT - OVERLAY_PADDING, PADDING_TOP))

    # Display the map boundaries (min and max x/y coordinates)
    bounds_text = f"X: {min_x} - {max_x}    Y: {min_y} - {max_y}"
    bounds_surf = font.render(bounds_text, True, WHITE)
    bounds_rect = bounds_surf.get_rect(topright=(WINDOW_WIDTH - PADDING_RIGHT - OVERLAY_PADDING, text_rect.bottom + LINE_SPACING))

    # Create background for the overlay and add text
    overlay_width = max(text_rect.width, bounds_rect.width) + 2 * OVERLAY_PADDING
    overlay_height = bounds_rect.bottom - text_rect.top + 2 * OVERLAY_PADDING
    overlay_x = WINDOW_WIDTH - overlay_width - PADDING_RIGHT
    overlay_y = text_rect.top - OVERLAY_PADDING

    overlay_bg = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
    overlay_bg.set_alpha(OVERLAY_BG_ALPHA)
    overlay_bg.fill((0, 0, 0))

    # Draw the overlay background and text
    screen.blit(overlay_bg, (overlay_x, overlay_y))
    screen.blit(text_surf, text_rect)
    screen.blit(bounds_surf, bounds_rect)


# === Initialization ===
# Initialize Pygame
pygame.init()
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
# Get screen dimensions
info = pygame.display.Info()
WINDOW_WIDTH = info.current_w or 1280
WINDOW_HEIGHT = info.current_h or 720
# Create the screen surface
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
# Set the window title
pygame.display.set_caption("OSRS Map Viewer")
# Handle events before entering the main loop
pygame.event.pump()
# Maximize the window
Window.from_display_module().maximize()

# === Initial Load: just Z=0 ===
# Load initial tiles for stage 1 (Z=0)
tile_images, min_x, max_x, min_y, max_y = load_tiles(BASE_DIR, stage=1)
print(f"Initial tile_images loaded: {len(tile_images)}")
# Initialize variables for dragging and zooming
dragging = False
drag_start = (0, 0)
offset = [0, 0]
zoom = 1.0
zoom_target = zoom
current_z = 0
MIN_Z = 0
MAX_Z = 3

# Set the initial offset to center the map on the starting tile
offset[0] = WINDOW_WIDTH // 2 - int((CENTER_TILE[0] - min_x + 0.5) * TILE_SIZE)
offset[1] = WINDOW_HEIGHT // 2 - int((max_y - CENTER_TILE[1] + 0.5) * TILE_SIZE)


# Main loop function
def main():
    global zoom, offset, tile_images, min_x, max_x, min_y, max_y
    # Initialize the clock for controlling the frame rate
    clock = pygame.time.Clock()
    running = True
    stage = 1
    stage_delay = 60
    frame_counter = 0

    while running:
        # Handle input events (mouse, keyboard)
        if not handle_events():
            break

        # Handle zoom adjustments (smooth transition)
        if abs(zoom - zoom_target) > 0.001:
            old_zoom = zoom
            if zoom < zoom_target:
                zoom = min(zoom + ZOOM_SPEED, zoom_target)
            elif zoom > zoom_target:
                zoom = max(zoom - ZOOM_SPEED, zoom_target)

            # Update offset based on zoom change
            mx, my = pygame.mouse.get_pos()
            offset[0] = mx - (mx - offset[0]) * (zoom / old_zoom)
            offset[1] = my - (my - offset[1]) * (zoom / old_zoom)

        # Handle stage transition (e.g., from stage 1 to stage 2)
        if stage == 1:
            frame_counter += 1
            if frame_counter >= stage_delay:
                frame_counter = 0
                new_tiles, mnx, mxx, mny, mxy = load_tiles(BASE_DIR, stage=2)
                print(f"Transitioned to stage 2, loaded {len(new_tiles)} new tiles.")
                tile_images.update(new_tiles)
                min_x = min(min_x, mnx)
                max_x = max(max_x, mxx)
                min_y = min(min_y, mny)
                max_y = max(max_y, mxy)
                stage = 2
                continue

        # Render the screen with black background
        screen.fill((0, 0, 0))
        # Draw map tiles and grid
        draw_tiles_and_grid()
        # Draw overlay (zoom and bounds info)
        draw_overlay()
        # Update the display
        pygame.display.flip()
        # Limit frame rate
        clock.tick(60)

    # Quit Pygame when the loop ends
    pygame.quit()


# Run the main function if this script is executed
if __name__ == "__main__":
    main()
