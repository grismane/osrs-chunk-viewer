import pygame
import os

# Setup
BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"
TARGET_COLOR = (0, 0, 0)
TILE_SIZE = 256  # assuming all images are this size

def is_uniform_color(image, target_color):
    """Check if the entire image matches the target color."""
    width, height = image.get_size()
    for y in range(height):
        for x in range(width):
            if image.get_at((x, y))[:3] != target_color:
                return False
    return True

def main():
    pygame.init()
    pygame.display.set_mode((1, 1))  # required for convert()

    deleted_count = 0
    total_checked = 0

    for z in range(4):  # Folders 0–3
        z_dir = os.path.join(BASE_DIR, str(z))
        if not os.path.isdir(z_dir):
            print(f"Missing directory: {z_dir}")
            continue

        for filename in os.listdir(z_dir):
            if not filename.endswith(".png"):
                continue

            path = os.path.join(z_dir, filename)
            total_checked += 1

            try:
                image = pygame.image.load(path).convert()
            except Exception as e:
                print(f"Failed to load {path}: {e}")
                continue

            if is_uniform_color(image, TARGET_COLOR):
                os.remove(path)
                deleted_count += 1
                print(f"Deleted: {path}")

    pygame.quit()

    print("\n--- Done ---")
    print(f"Total files checked: {total_checked}")
    print(f"Tiles deleted (color {TARGET_COLOR}): {deleted_count}")

if __name__ == "__main__":
    main()
