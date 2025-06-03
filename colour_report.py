import pygame
import sys
from collections import Counter

def analyze_image_colors(image_path):
    pygame.init()
    # Minimal window to satisfy pygame's video requirements
    pygame.display.set_mode((1, 1))

    try:
        image = pygame.image.load(image_path)
    except Exception as e:
        print(f"Failed to load image {image_path}: {e}")
        pygame.quit()
        return

    # Convert image for pixel access
    image = image.convert()

    width, height = image.get_size()
    pixel_colors = []

    for y in range(height):
        for x in range(width):
            color = image.get_at((x, y))
            pixel_colors.append((color.r, color.g, color.b))

    pygame.quit()

    color_counts = Counter(pixel_colors)

    print(f"Color report for image: {image_path}")
    print(f"Total pixels: {width * height}")
    print(f"Unique colors found: {len(color_counts)}")
    print("Most common colors (top 10):")
    for color, count in color_counts.most_common(10):
        print(f"  Color {color} - {count} pixels")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 colour_report.py <image_path>")
    else:
        analyze_image_colors(sys.argv[1])

# python3 colour_report.py /mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22/0/2_31_77.png