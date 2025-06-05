import os  # file system
import pygame

from queue import PriorityQueue
import threading
import time

# === Constants ===
# Map tiles
MAP_TILE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"
Z_MIN = 0
Z_MAX = 3
X_MIN = 16
X_MAX = 65
Y_MIN = 19
Y_MAX = 196
TILE_SIZE = 256

# Initial map tile loading
INIT_CENTER = (50, 50)  # initial focus tile
VIEWPORT_RADIUS = 4
INIT_X_MIN = INIT_CENTER[0] - VIEWPORT_RADIUS
INIT_X_MAX = INIT_CENTER[0] + VIEWPORT_RADIUS
INIT_Y_MIN = INIT_CENTER[1] - VIEWPORT_RADIUS
INIT_Y_MAX = INIT_CENTER[1] + VIEWPORT_RADIUS
INIT_Z = 0

# Zoom levels
ZOOM_LEVELS = [4.0, 2.0, 1.0, 0.5, 0.25, 0.125]
ZOOM_SPEED = 0.02  # percent zoom per frame

# Color constants for rendering
BACKGROUND_COLOUR = (0, 0, 0)
GRID_LINE_COLOUR = (255, 255, 255)
BACKGROUND_LINE_COLOUR = (51, 51, 51)

# Constants for overlay layout and appearance
PADDING_RIGHT = 32
PADDING_TOP = 32
LINE_SPACING = 8
OVERLAY_PADDING = 16
OVERLAY_BG_ALPHA = 128
FONT_SIZE = 48


# === Viewer State Class ===
class ViewerState:
    def __init__(self, screen, window_size):
        self.screen = screen
        self.window_width, self.window_height = window_size
        self.zoom = 1.0
        self.zoom_target = 1.0
        self.current_z = 0
        self.offset = [0, 0]  # x and y scroll offset
        self.dragging = False
        self.drag_start = (0, 0)



# === Initialization Functions ===
def initialize_window():
    os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
    os.environ["SDL_AUDIODRIVER"] = "dummy"  # set a dummy audio output to avoid error in pygame
    
    pygame.init()
    
    info = pygame.display.Info()  # Get screen dimensions
    window_size = (info.current_w - 12, info.current_h - 82)
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)  # Create the screen surface
    pygame.display.set_caption("OSRS Map Viewer")
        
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # Loading screen
    screen.fill(BACKGROUND_COLOUR)  # Clear background
    font = pygame.font.SysFont(None, FONT_SIZE)
    loading_text = "Loading..."
    loading_text_surf = font.render(loading_text, True, GRID_LINE_COLOUR)
    loading_text_rect = loading_text_surf.get_rect(center=(window_size[0] / 2, window_size[1] / 2))
    screen.blit(loading_text_surf, loading_text_rect)
    pygame.display.flip()

    return screen, window_size


def compute_priority(x, y, z, viewport_x, viewport_y, viewport_z):
    dz = abs(z - viewport_z)
    dx = abs(x - viewport_x)
    dy = abs(y - viewport_y)
    return dz * 1000 + dx + dy  # Weight z distance higher if needed


def init_load():
    loaded_tiles = {}  # dictionary of loaded tile images

    for x in range(INIT_X_MIN, INIT_X_MAX + 1):
        for y in range(INIT_Y_MIN, INIT_Y_MAX + 1):
            filename = f"{INIT_Z}_{x}_{y}.png"
            img_path = os.path.join(MAP_TILE_DIR, filename)
            if not os.path.exists(img_path):
                continue

            try:
                surface = pygame.image.load(img_path)
                image = surface.convert()
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                image = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert()
                image.fill(BACKGROUND_COLOUR)

            loaded_tiles[(INIT_Z, x, y)] = image

    print(f"Loaded {len(loaded_tiles)} initial tiles.")  # Total number of tiles loaded at this time
    return loaded_tiles


def tile_loader_thread(tile_queue, loaded_tiles, tile_lock):
    while not tile_queue.empty():
        priority, (z, x, y) = tile_queue.get()

        filename = f"{z}_{x}_{y}.png"
        path = os.path.join(MAP_TILE_DIR, filename)

        if not os.path.exists(path):
            continue

        try:
            surface = pygame.image.load(path)
            image = surface.convert()
            with tile_lock:
                loaded_tiles[(z, x, y)] = image
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue

        time.sleep(0.001)  # Yield to UI thread


# === Rendering Functions ===
def draw_tiles_and_grid(screen, loaded_tiles, offset, zoom, current_z, window_size, tile_lock):
    tile_size_zoomed = TILE_SIZE * zoom
    visible_rect = pygame.Rect(0, 0, *window_size)

    screen.fill(BACKGROUND_COLOUR)  # Clear background

    with tile_lock:
        for (z, x, y), image in loaded_tiles.items():
            if not isinstance(image, pygame.Surface) or z != current_z:
                continue

            draw_x = (x - X_MIN) * tile_size_zoomed + offset[0]
            draw_y = (Y_MAX - y) * tile_size_zoomed + offset[1]
            tile_rect = pygame.Rect(draw_x, draw_y, tile_size_zoomed, tile_size_zoomed)

            if not visible_rect.colliderect(tile_rect):
                continue

            # Scale and blit the tile
            scaled = pygame.transform.smoothscale(image, (int(tile_size_zoomed), int(tile_size_zoomed)))
            screen.blit(scaled, tile_rect)

            # Draw a white outline around the tile
            pygame.draw.rect(screen, GRID_LINE_COLOUR, tile_rect, 1)


def draw_overlay(screen, window_size, state, all_tiles_loaded):
    font = pygame.font.SysFont(None, FONT_SIZE)

    # --- Zoom level and floor ---
    zoom_text = f"Zoom: {state.zoom:.2f}x"
    floor_text = f"Floor (Z): {state.current_z}"
    lines = [zoom_text, floor_text]

    for i, text in enumerate(lines):
        text_surf = font.render(text, True, GRID_LINE_COLOUR)
        screen.blit(text_surf, (PADDING_RIGHT, PADDING_TOP + i * (FONT_SIZE + LINE_SPACING)))

    # --- Loading message ---
    if not all_tiles_loaded:
        loading_text = "Loading map tiles..."
        loading_surf = font.render(loading_text, True, GRID_LINE_COLOUR)

        overlay_width = loading_surf.get_width() + 2 * OVERLAY_PADDING
        overlay_height = loading_surf.get_height() + 2 * OVERLAY_PADDING
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, OVERLAY_BG_ALPHA))
        overlay.blit(loading_surf, (OVERLAY_PADDING, OVERLAY_PADDING))

        pos_x = (window_size[0] - overlay_width) // 2
        pos_y = window_size[1] - overlay_height - PADDING_TOP
        screen.blit(overlay, (pos_x, pos_y))


# === Event Handling ===
def handle_events(state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            state.dragging = True
            state.drag_start = event.pos
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            state.dragging = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        elif event.type == pygame.MOUSEMOTION and state.dragging:
            dx = event.pos[0] - state.drag_start[0]
            dy = event.pos[1] - state.drag_start[1]
            state.offset[0] += dx
            state.offset[1] += dy
            state.drag_start = event.pos

        elif event.type == pygame.MOUSEWHEEL:
            try:
                idx = ZOOM_LEVELS.index(state.zoom_target)
            except ValueError:
                closest = min(ZOOM_LEVELS, key=lambda z: abs(z - state.zoom_target))
                idx = ZOOM_LEVELS.index(closest)

            if event.y > 0 and idx > 0:
                state.zoom_target = ZOOM_LEVELS[idx - 1]
            elif event.y < 0 and idx < len(ZOOM_LEVELS) - 1:
                state.zoom_target = ZOOM_LEVELS[idx + 1]

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and state.current_z < Z_MAX:
                state.current_z += 1
            elif event.key == pygame.K_DOWN and state.current_z > Z_MIN:
                state.current_z -= 1

    return True


# === Main Loop ===
def main():
    screen, window_size = initialize_window()
    state = ViewerState(screen, window_size)

    tile_lock = threading.Lock()
    tile_queue = PriorityQueue()

    print("Loading tiles...")
    loaded_tiles = init_load()

    for z in range(Z_MIN, Z_MAX + 1):
        for x in range(X_MIN, X_MAX + 1):
            for y in range(Y_MIN, Y_MAX + 1):
                key = (z, x, y)
                if key in loaded_tiles:
                    continue
                priority = compute_priority(x, y, z, INIT_CENTER[0], INIT_CENTER[1], INIT_Z)
                tile_queue.put((priority, key))

    # Launch thread and keep reference
    tile_thread = threading.Thread(
        target=tile_loader_thread, args=(tile_queue, loaded_tiles, tile_lock), daemon=True)
    tile_thread.start()
    all_tiles_loaded = False

    # Center map on the initial tile
    state.offset[0] = state.window_width // 2 - int((INIT_CENTER[0] - X_MIN + 0.5) * TILE_SIZE)
    state.offset[1] = state.window_height // 2 - int((Y_MAX - INIT_CENTER[1] + 0.5) * TILE_SIZE)

    running = True
    while running:
        if not handle_events(state):
            break

        if not all_tiles_loaded and not tile_thread.is_alive():
            print(f"Loaded {len(loaded_tiles)} tiles. Loading complete ✅")
            all_tiles_loaded = True

        # Handle zoom smooth transition
        if abs(state.zoom - state.zoom_target) > 0.001:
            old_zoom = state.zoom
            if state.zoom < state.zoom_target:
                state.zoom = min(state.zoom + ZOOM_SPEED, state.zoom_target)
            elif state.zoom > state.zoom_target:
                state.zoom = max(state.zoom - ZOOM_SPEED, state.zoom_target)

            # Zoom focal point is the mouse location
            mx, my = pygame.mouse.get_pos()
            state.offset[0] = mx - (mx - state.offset[0]) * (state.zoom / old_zoom)
            state.offset[1] = my - (my - state.offset[1]) * (state.zoom / old_zoom)

        draw_tiles_and_grid(
            screen, loaded_tiles, state.offset, state.zoom, 
            state.current_z, window_size, tile_lock)
        draw_overlay(screen, window_size, state, all_tiles_loaded)
        pygame.display.flip()  # Update the screen

    pygame.quit()


if __name__ == "__main__":
    main()
