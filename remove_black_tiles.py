import pygame
import os

# Constants
TILE_SIZE = 256
BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22_a/-1"

def is_surface_black(surface):
    """Check if the entire surface is black (all pixels are (0,0,0))."""
    surface.lock()
    width, height = surface.get_size()
    for x in range(width):
        for y in range(height):
            if surface.get_at((x, y))[:3] != (0, 0, 0):
                surface.unlock()
                return False
    surface.unlock()
    return True

def main():
    pygame.init()

    # Set a minimal display mode to enable .convert() calls
    pygame.display.set_mode((1, 1))

    removed_files = 0
    total_files = 0

    for z in range(0, 4):
        z_dir = os.path.join(BASE_DIR, str(z))
        if not os.path.isdir(z_dir):
            print(f"Warning: Missing directory for Z={z}: {z_dir}")
            continue

        for filename in os.listdir(z_dir):
            if filename.endswith(".png"):
                total_files += 1
                img_path = os.path.join(z_dir, filename)
                try:
                    image = pygame.image.load(img_path).convert()
                    if is_surface_black(image):
                        print(f"Deleting black tile: {img_path}")
                        os.remove(img_path)
                        removed_files += 1
                except Exception as e:
                    print(f"Error loading {img_path}: {e}")

    pygame.quit()
    print(f"--- Done ---")
    print(f"Total files checked: {total_files}")
    print(f"Black tiles removed: {removed_files}")

if __name__ == "__main__":
    main()
