import pygame
import os
from collections import Counter

BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"

def is_uniform_dark(image, max_lum=16):
    """
    Checks if the image is uniformly one dark color with R=G=B <= max_lum.
    Returns the grayscale value if true, else None.
    """
    width, height = image.get_size()
    first_color = image.get_at((0, 0))
    r, g, b = first_color.r, first_color.g, first_color.b

    if r != g or g != b or r > max_lum:
        return None

    for y in range(height):
        for x in range(width):
            c = image.get_at((x, y))
            if (c.r, c.g, c.b) != (r, g, b):
                return None
    return r

def main():
    pygame.init()
    pygame.display.set_mode((1,1))  # Minimal display for .convert()

    dark_counts = Counter()
    total_images = 0

    for z in range(4):
        folder = os.path.join(BASE_DIR, str(z))
        if not os.path.isdir(folder):
            print(f"Warning: Missing directory {folder}")
            continue
        for filename in os.listdir(folder):
            if not filename.endswith(".png"):
                continue
            total_images += 1
            path = os.path.join(folder, filename)
            try:
                image = pygame.image.load(path).convert()
            except Exception as e:
                print(f"Failed to load {path}: {e}")
                continue

            gray_level = is_uniform_dark(image)
            if gray_level is not None:
                dark_counts[gray_level] += 1

    pygame.quit()

    print(f"--- Dark Uniform Images Report ---")
    print(f"Total images checked: {total_images}")
    if dark_counts:
        for level in sorted(dark_counts):
            print(f"Grayscale ({level}, {level}, {level}): {dark_counts[level]} images")
    else:
        print("No uniformly dark images found.")

if __name__ == "__main__":
    main()
