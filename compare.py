import cv2
import os
from pathlib import Path
import shutil
import numpy as np

def compare_images(prev_image, current_image):
    # Convert to grayscale
    prev_gray = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference
    diff = cv2.absdiff(prev_gray, curr_gray)

    # Apply noise filter
    noise_mask = diff <= 4
    filtered_diff = diff.copy()
    filtered_diff[noise_mask] = 0

    # Find contours on the filtered difference image
    contours, _ = cv2.findContours(filtered_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by area and calculate total change area
    significant_contours = [c for c in contours if cv2.contourArea(c) > 50]  # Adjust as needed
    total_change_area = sum(cv2.contourArea(c) for c in significant_contours)

    # Calculate the change percentage
    total_pixels = curr_gray.shape[0] * curr_gray.shape[1]
    change_percentage = (total_change_area / total_pixels) * 100  # Convert to percentage

    return change_percentage, len(significant_contours), significant_contours

def process_images(source_dir, del_dir):
    # Ensure the DEL directory exists
    Path(del_dir).mkdir(parents=True, exist_ok=True)

    # Get a sorted list of image files
    image_files = sorted([f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    if not image_files:
        print("No image files found in the source directory.")
        return

    prev_image = None
    for i, filename in enumerate(image_files):
        current_image_path = os.path.join(source_dir, filename)
        current_image = cv2.imread(current_image_path)

        if prev_image is not None:
            change_percentage, num_contours, significant_contours = compare_images(prev_image, current_image)
            
            print(f"\nComparing {image_files[i-1]} to {filename}:")
            print(f"  Change percentage: {change_percentage:.2f}%")
            print(f"  Number of significant contours: {num_contours}")
            
            # Print details of the top 5 largest contours
            if num_contours > 0:
                sorted_contours = sorted(significant_contours, key=cv2.contourArea, reverse=True)
                print("  Top 5 largest contours (area in pixels):")
                for j, contour in enumerate(sorted_contours[:5], 1):
                    print(f"    Contour {j}: {cv2.contourArea(contour):.0f}")
            
            should_keep = 0.1 < change_percentage < 50
            if not should_keep:
                # Move to DEL directory
                shutil.move(current_image_path, os.path.join(del_dir, filename))
                print(f"  Result: Moved {filename} to DEL directory")
            else:
                print(f"  Result: Kept {filename} in original directory")
        else:
            print(f"\nKept {filename} (first image)")

        prev_image = current_image

    print("\nProcessing complete.")

if __name__ == "__main__":
    source_dir = "/home/camera/Mothcam/Pictures"
    del_dir = "/home/camera/Mothcam/DEL"
    process_images(source_dir, del_dir)
