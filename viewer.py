import pygame
from pygame._sdl2 import Window 
import os

# Constants
TILE_SIZE = 256
IMAGE_DIR = "map/2025-05-22"

# Load image file names and calculate map bounds
tile_images = {}
min_x = min_y = float("inf")
max_x = max_y = float("-inf")

for filename in os.listdir(IMAGE_DIR):
    if filename.endswith(".png"):
        parts = filename[:-4].split("_")
        if len(parts) == 3:
            try:
                z, x, y = map(int, parts)
                img_path = os.path.join(IMAGE_DIR, filename)
                image = pygame.image.load(img_path)
            except Exception as e:
                print(f"Problem loading {filename}, using black square instead: {e}")
                image = pygame.Surface((TILE_SIZE, TILE_SIZE))
                image.fill((0, 0, 0))  # Black fallback
            tile_images[(x, y)] = image
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

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                dragging = True
                drag_start = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                dx = event.pos[0] - drag_start[0]
                dy = event.pos[1] - drag_start[1]
                offset[0] += dx
                offset[1] += dy
                drag_start = event.pos

    screen.fill((0, 0, 0))  # Black background

    for (x, y), image in tile_images.items():
        draw_x = (x - min_x) * TILE_SIZE + offset[0]
        draw_y = (max_y - y) * TILE_SIZE + offset[1]  # Flip Y so larger Y is higher

        # Only draw if it's on screen
        if (-TILE_SIZE < draw_x < WINDOW_WIDTH and -TILE_SIZE < draw_y < WINDOW_HEIGHT):
            screen.blit(image, (draw_x, draw_y))

    # Draw vertical grid lines
    for x in range(min_x, max_x + 2):
        start_x = (x - min_x) * TILE_SIZE + offset[0]
        pygame.draw.line(screen, (255, 255, 255), (start_x, 0), (start_x, WINDOW_HEIGHT), 1)

    # Draw horizontal grid lines
    for y in range(min_y, max_y + 2):
        start_y = (max_y - y + 1) * TILE_SIZE + offset[1]
        pygame.draw.line(screen, (255, 255, 255), (0, start_y), (WINDOW_WIDTH, start_y), 1)


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
