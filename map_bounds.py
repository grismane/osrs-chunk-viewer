import os
import re

BASE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"

def get_bounds(base_dir):
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    total_files = 0

    pattern = re.compile(r"(\d+)_(\d+)_(\d+)")  # Matches first 3 numeric parts

    for z in range(4):  # Folders 0 to 3
        z_dir = os.path.join(base_dir, str(z))
        if not os.path.isdir(z_dir):
            print(f"Missing folder: {z_dir}")
            continue

        for filename in os.listdir(z_dir):
            if not filename.lower().endswith(".png"):
                continue

            match = pattern.match(filename)
            if not match:
                print(f"Skipping unrecognized filename: {filename}")
                continue

            try:
                z_str, x_str, y_str = match.groups()
                x, y = int(x_str), int(y_str)
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                total_files += 1
            except Exception as e:
                print(f"Error parsing {filename}: {e}")

    if total_files == 0:
        print("No valid tile files found.")
    else:
        print(f"--- Map Bounds ---")
        print(f"Total tiles scanned: {total_files}")
        print(f"X: {min_x} - {max_x}")
        print(f"Y: {min_y} - {max_y}")

if __name__ == "__main__":
    get_bounds(BASE_DIR)
