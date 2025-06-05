import os
import re
import pygame
import shutil
from collections import Counter

MAP_TILE_DIR = "/mnt/c/Users/andre/Downloads/OSRS_map_rip/2025-05-22"
TILE_SIZE = 256

# === Map Bounds Function ===
def get_bounds():
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    total_files = 0

    # Loop through each file in the base directory
    for filename in os.listdir(MAP_TILE_DIR):
        if not filename.lower().endswith(".png"):
            continue  # Only process .png files

        # Split the filename like 'z_x_y.png' into its components
        try:
            parts = filename.lower().split('_')
            z, x_str, y_str_with_ext = parts[0], parts[1], parts[2]
            y_str = y_str_with_ext.split('.')[0]

            x, y = int(x_str), int(y_str)

            # Update bounds
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            total_files += 1
        except ValueError as e:
            print(f"Skipping invalid filename {filename}: {e}")
            continue

    if total_files == 0:
        print("No valid tile files found.")
    else:
        print(f"--- Map Bounds ---")
        print(f"Total tiles scanned: {total_files}")
        print(f"X: {min_x} - {max_x}")
        print(f"Y: {min_y} - {max_y}")


# === Format Names Function ===
def format_names():
    """Renames all images in the base directory to the format [z]_[x]_[y].png, removing extra text."""
    # Loop through all files in the base directory
    for filename in os.listdir(MAP_TILE_DIR):
        if filename.lower().endswith(".png"):  # Only process .png files
            # Regular expression to capture the correct format [z]_[x]_[y] and remove anything after
            # We need to match the whole pattern [z]_[x]_[y] and eliminate the extra text after it
            new_filename = re.sub(r"^(\d+_\d+_\d+)[^\.]*\.png$", r"\1.png", filename)

            # If the filename has changed, rename the file
            if new_filename != filename:
                old_path = os.path.join(MAP_TILE_DIR, filename)
                new_path = os.path.join(MAP_TILE_DIR, new_filename)

                try:
                    os.rename(old_path, new_path)
                    print(f"Renamed {filename} to {new_filename}")
                except Exception as e:
                    print(f"Failed to rename {filename} to {new_filename}: {e}")


# === Find Monochrome Function ===
def is_uniform_color(image):
    """Check if the entire image matches a single color (uniform)."""
    width, height = image.get_size()
    first_color = image.get_at((0, 0))
    r, g, b = first_color.r, first_color.g, first_color.b

    for y in range(height):
        for x in range(width):
            c = image.get_at((x, y))
            if (c.r, c.g, c.b) != (r, g, b):
                return None
    return (r, g, b)  # Return the uniform color as an RGB tuple


def find_monochrome():
    """Find and report all uniformly colored images in the base directory."""
    os.environ["SDL_AUDIODRIVER"] = "dummy"  # set a dummy audio output to avoid error in pygame
    pygame.init()
    pygame.display.set_mode((1, 1))  # Dummy display required for surface creation

    color_counts = Counter()
    color_images = {}  # Dictionary to store color -> list of image paths
    total_images = 0

    print("\nFinding monochrome tiles...\n")

    # Loop through each file in the base directory
    for filename in os.listdir(MAP_TILE_DIR):
        if not filename.lower().endswith(".png"):
            continue  # Only process .png files

        path = os.path.join(MAP_TILE_DIR, filename)
        total_images += 1
        try:
            image = pygame.image.load(path).convert()  # Convert for faster access
        except Exception as e:
            print(f"Failed to load {path}: {e}")
            continue

        # Check if the image is uniformly one color
        color = is_uniform_color(image)
        if color is not None:
            color_counts[color] += 1  # Increment the count for this color
            if color not in color_images:
                color_images[color] = []
            color_images[color].append(path)  # Store the image path for this color

    pygame.quit()

    # Output the results
    print(f"--- Uniform Color Images Report ---")
    print(f"Total images checked: {total_images}")
    if color_counts:
        color_list = list(color_counts.items())
        color_list.sort(key=lambda c: c[1], reverse=True)

        # Display list of colors and their counts, assign numbers
        for idx, (color, count) in enumerate(color_list, start=1):
            print(f"{idx}. {color}: {count} images")

        # Allow user to select color to move
        move_images(color_list, color_images)
    else:
        print("No uniformly colored images found.")


# === Move Monochrome Images to Folders ===
def move_images(color_list, color_images):
    """Move images of the selected color to a folder based on color."""
    while True:
        try:
            choice = input("\nEnter the number to move images, or '0' to exit: ").strip().lower()

            if choice == '0':
                print("Exiting to main menu.")
                return

            choice = int(choice) - 1  # Adjust for 0-based indexing

            if choice < 0 or choice >= len(color_list):
                print("Invalid selection. Try again.")
                continue

            color, _ = color_list[choice]
            # Create a folder for the color in the base directory (e.g., '43, 54, 78')
            color_folder = f"{color[0]}, {color[1]}, {color[2]}"
            color_folder_path = os.path.join(MAP_TILE_DIR, color_folder)

            # Ensure the folder exists
            os.makedirs(color_folder_path, exist_ok=True)

            # Move images of the selected color to the corresponding folder
            images_to_move = color_images.get(color, [])
            if not images_to_move:
                print(f"No images found for the color {color}.")
                continue

            # Move each image to the respective folder
            for img_path in images_to_move:
                dest_path = os.path.join(color_folder_path, os.path.basename(img_path))
                shutil.move(img_path, dest_path)
                print(f"Moved {os.path.basename(img_path)} to {color_folder_path}")

            # Remove the moved images from the color_images dictionary
            color_images.pop(color, None)

            # After moving, reprint the monochrome color report
            print(f"\n--- Updated Uniform Color Images Report ---")
            if color_images:
                for idx, (color, paths) in enumerate(color_images.items(), start=1):
                    print(f"{idx}. {color}: {len(paths)} images")
            else:
                print("No monochrome images left.")
                
            # Ask if you want to move more or exit
            continue_choice = input("Would you like to move another color? (y/n): ").strip().lower()
            if continue_choice != 'y':
                print("Exiting to main menu.")
                return

        except ValueError:
            print("Please enter a valid number or 'esc' to exit.")



# === Remove Corrupt Function ===
def remove_corrupt():
    """Move corrupt or unreadable images to a separate folder by rendering them as black squares."""
    os.environ["SDL_AUDIODRIVER"] = "dummy"  # set a dummy audio output to avoid error in pygame
    pygame.init()
    pygame.display.set_mode((1, 1))  # Dummy display required for surface creation

    MONOCHROME_DIR = os.path.join(MAP_TILE_DIR, "corrupt_pngs")
    os.makedirs(MONOCHROME_DIR, exist_ok=True)

    total_images = 0
    moved_images = 0

    # Loop through each file in the base directory
    for filename in os.listdir(MAP_TILE_DIR):
        if not filename.lower().endswith(".png"):
            continue  # Only process .png files

        img_path = os.path.join(MAP_TILE_DIR, filename)
        total_images += 1

        try:
            # Try to load the image
            surface = pygame.image.load(img_path)
            if surface.get_alpha() is not None:
                image = surface.convert_alpha()  # Handle images with transparency
            else:
                image = surface.convert()  # Handle regular images without transparency
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            
            # If there is an error loading the image, create a black placeholder image
            image = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert()
            image.fill((0, 0, 0))  # Fill it with black color (corrupt image placeholder)

            # Move the corrupt image to the 'corrupt_pngs' folder
            dest_path = os.path.join(MONOCHROME_DIR, filename)
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(filename)
                count = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(MONOCHROME_DIR, f"{base}_{count}{ext}")
                    count += 1
            shutil.move(img_path, dest_path)
            moved_images += 1

    pygame.quit()

    print(f"\n--- Corrupt Image Report ---")
    print(f"Total files scanned: {total_images}")
    print(f"Moved {moved_images} corrupt or unreadable images to: {MONOCHROME_DIR}")


# === Main Menu ===
def main():
    while True:
        print("\nMain Menu:")
        print("1. Map Bounds")
        print("2. Find Monochrome Images")
        print("3. Remove Corrupt Images")
        print("4. Format Image Names")  # Add the new option here
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            get_bounds()
        elif choice == '2':
            find_monochrome()
        elif choice == '3':
            remove_corrupt()
        elif choice == '4':  # Option to run the format_names function
            format_names()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
