import pygame
from pygame._sdl2 import Window 
import os

# Constants
TILE_SIZE = 256

# Load image file names from folders 0 to 3 and calculate map bounds
tile_images = {}  # Keys: (z, x, y)
min_x = min_y = float("inf")
max_x = max_y = float("-inf")

BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22_a/-1"
for z in range(0, 4):  # Floors 0 to 3
    z_dir = os.path.join(BASE_DIR, str(z))
    if not os.path.isdir(z_dir):
        print(f"Warning: Missing directory for Z={z}: {z_dir}")
        continue

    for filename in os.listdir(z_dir):
        if filename.endswith(".png"):
            parts = filename[:-4].split("_")
            if len(parts) == 3:
                try:
                    _, x, y = map(int, parts)  # Discard Z from filename since it's implied by folder
                    img_path = os.path.join(z_dir, filename)
                    image = pygame.image.load(img_path)
                except Exception as e:
                    print(f"Problem loading {filename} at Z={z}, using black square: {e}")
                    image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                    image.fill((0, 0, 0))


                tile_images[(z, x, y)] = image
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

# Get screen size
pygame.init()
pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW) # use normal Windows Cursor
info = pygame.display.Info()
WINDOW_WIDTH = info.current_w
WINDOW_HEIGHT = info.current_h

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("OSRS Map Viewer")
window = Window.from_display_module()
window.maximize()

# Drag state
dragging = False
drag_start = (0, 0)
offset = [0, 0]  # x, y

zoom = 1.0
ZOOM_MIN = 0.25
ZOOM_MAX = 4.0
ZOOM_STEP = 0.1

current_z = 0  # Start at Z = 0
MAX_Z = 3
MIN_Z = 0

clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont(None, 24)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:  # left click press
            if event.button == 1:  # Left click
                dragging = True
                drag_start = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:    # left click release
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION:      # mouse dragging
            if dragging:
                dx = event.pos[0] - drag_start[0]
                dy = event.pos[1] - drag_start[1]
                offset[0] += dx
                offset[1] += dy
                drag_start = event.pos

        elif event.type == pygame.KEYDOWN:          # up and down arrow keys
            if event.key == pygame.K_UP and current_z < MAX_Z:
                current_z += 1
            elif event.key == pygame.K_DOWN and current_z > MIN_Z:
                current_z -= 1
        
        elif event.type == pygame.MOUSEWHEEL:       # mouse wheel
            old_zoom = zoom
            if event.y > 0 and zoom < ZOOM_MAX:
                zoom += ZOOM_STEP
            elif event.y < 0 and zoom > ZOOM_MIN:
                zoom -= ZOOM_STEP
            zoom = max(ZOOM_MIN, min(ZOOM_MAX, round(zoom, 2)))

            # zoom around mouse pointer
            mx, my = pygame.mouse.get_pos()
            offset[0] = mx - (mx - offset[0]) * (zoom / old_zoom)
            offset[1] = my - (my - offset[1]) * (zoom / old_zoom)



    screen.fill((0, 0, 0))  # Black background

    # floor number and zoom % display in top right corner
    text = f"Floor: {current_z}    Zoom: {int(zoom * 100)}%"
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(topright=(WINDOW_WIDTH - 10, 10))

    # semi-transparent background behind text
    overlay_bg = pygame.Surface((text_rect.width + 10, text_rect.height + 6))
    overlay_bg.set_alpha(128)
    overlay_bg.fill((0, 0, 0))
    screen.blit(overlay_bg, (text_rect.right - overlay_bg.get_width(), text_rect.top - 3))
    screen.blit(text_surf, text_rect)

    for (z, x, y), image in tile_images.items():
        if z != current_z:
            continue

        draw_x = (x - min_x) * TILE_SIZE * zoom + offset[0]
        draw_y = (max_y - y) * TILE_SIZE * zoom + offset[1]


        # Only draw if it's on screen
        tile_size_zoomed = TILE_SIZE * zoom
        if (-tile_size_zoomed < draw_x < WINDOW_WIDTH and -tile_size_zoomed < draw_y < WINDOW_HEIGHT):
            scaled_image = pygame.transform.smoothscale(image, (int(TILE_SIZE * zoom), int(TILE_SIZE * zoom)))
            screen.blit(scaled_image, (draw_x, draw_y))


    # Draw vertical grid lines
    for x in range(min_x, max_x + 2):
        start_x = (x - min_x) * TILE_SIZE * zoom + offset[0]
        pygame.draw.line(screen, (255, 255, 255), (start_x, 0), (start_x, WINDOW_HEIGHT), 1)

    # Draw horizontal grid lines
    for y in range(min_y, max_y + 2):
        start_y = (max_y - y + 1) * TILE_SIZE * zoom + offset[1]
        pygame.draw.line(screen, (255, 255, 255), (0, start_y), (WINDOW_WIDTH, start_y), 1)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
