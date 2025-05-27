import pygame
import os

# Initialize pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Dummy display required for .convert_alpha()

BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22_a/-1"
TILE_SIZE = 256

def check_image_format(path):
    try:
        image = pygame.image.load(path).convert_alpha()
        bits = image.get_bitsize()
        return bits
    except Exception as e:
        return f"Error: {e}"

def main():
    total_checked = 0
    bad_images = []

    for z in range(4):  # Floors 0 to 3
        z_dir = os.path.join(BASE_DIR, str(z))
        if not os.path.isdir(z_dir):
            print(f"Missing directory: {z_dir}")
            continue

        for filename in os.listdir(z_dir):
            if not filename.endswith(".png"):
                continue

            img_path = os.path.join(z_dir, filename)
            result = check_image_format(img_path)
            total_checked += 1

            # Log issues
            if result != 24 and result != 32:
                bad_images.append((img_path, result))

            # Only print progress every 100 images
            if total_checked % 100 == 0:
                print(f"{total_checked} images checked...")

    # Final report
    print("\n--- Format Check Complete ---")
    print(f"Total images checked: {total_checked}")
    print(f"Problematic images: {len(bad_images)}\n")

    if bad_images:
        print("List of problematic images:")
        for path, issue in bad_images:
            print(f" - {path} => {issue}")

if __name__ == "__main__":
    main()
    pygame.quit()
