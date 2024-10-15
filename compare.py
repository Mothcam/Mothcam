import os
import cv2
import numpy as np
from pathlib import Path
import shutil

def compare_images(img1, img2):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between the images
    diff = cv2.absdiff(gray1, gray2)

    # Apply noise filter
    noise_mask = diff <= 4
    diff[noise_mask] = 0

    # Calculate the difference percentage
    diff_percentage = (np.count_nonzero(diff) / diff.size) * 100

    return diff_percentage

def process_images(source_dir, dest_dir, similarity_threshold):
    source_path = Path(source_dir)
    dest_path = Path(dest_dir)
    
    # Ensure the destination directory exists
    dest_path.mkdir(parents=True, exist_ok=True)

    # Get all jpg files in the source directory
    image_files = sorted([f for f in source_path.glob('*.jpg')])

    prev_img = None
    prev_filename = None

    for current_file in image_files:
        curr_img = cv2.imread(str(current_file))

        if curr_img is None:
            print(f"Error reading image: {current_file}")
            continue

        if prev_img is not None:
            diff_percentage = compare_images(prev_img, curr_img)

            print(f"Difference between {prev_filename.name} and {current_file.name}: {diff_percentage:.2f}%")

            if diff_percentage <= similarity_threshold:
                # Move the current image to the DEL directory
                shutil.move(str(current_file), str(dest_path / current_file.name))
                print(f"Moved {current_file.name} to {dest_path}")
            else:
                # Update prev_img and prev_filename only if the current image is not moved
                prev_img = curr_img
                prev_filename = current_file
        else:
            # For the first image
            prev_img = curr_img
            prev_filename = current_file

def main():
    source_dir = "/home/camera/Mothcam/Pictures"
    dest_dir = "/home/camera/Mothcam/DEL"
    similarity_threshold = 1  # 1% difference threshold, adjust as needed

    process_images(source_dir, dest_dir, similarity_threshold)

if __name__ == "__main__":
    main()
