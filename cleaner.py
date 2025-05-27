import os
import shutil
import pygame

pygame.init()

SOURCE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22_a/-1"
CORRUPT_DIR = os.path.join(SOURCE_DIR, "corrupt_pngs")

os.makedirs(CORRUPT_DIR, exist_ok=True)

print(f"Scanning folder: {SOURCE_DIR}")

total_images = 0
moved_images = 0

for filename in os.listdir(SOURCE_DIR):
    if filename.lower().endswith(".png"):
        filepath = os.path.join(SOURCE_DIR, filename)

        # Skip if it's already in the corrupt folder
        if os.path.commonpath([filepath, CORRUPT_DIR]) == CORRUPT_DIR:
            continue

        total_images += 1
        try:
            if os.path.getsize(filepath) == 0:
                raise ValueError("File is empty (0 bytes)")
            pygame.image.load(filepath)
        except Exception as e:
            print(f"Corrupt or unreadable image found: {filename} ({e}), moving to corrupt_pngs")
            dest_path = os.path.join(CORRUPT_DIR, filename)
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                count = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(CORRUPT_DIR, f"{base}_{count}{ext}")
                    count += 1
            shutil.move(filepath, dest_path)
            moved_images += 1

print(f"Scanned {total_images} images.")
print(f"Moved {moved_images} corrupt or empty images to: {CORRUPT_DIR}")
print("Cleanup complete.")

pygame.quit()
