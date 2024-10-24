#!/usr/bin/python3
import cv2
import time
import json
import os
from pathlib import Path
import numpy as np
import multiprocessing as mp
from picamera2 import Picamera2
from libcamera import controls
from datetime import datetime
from queue import Empty


def to_bool(value):
	if isinstance(value, bool):
		return value
	if str(value).lower() in ("yes", "y", "true", "t", "1"):
		return True
	if str(value).lower() in ("no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
		return False
	raise ValueError(f"Invalid boolean value: {value}")


def get_base_paths():
	script_dir = Path(__file__).parent.resolve()
	default_config_path = script_dir / 'mothconfig.json'
	default_pictures_path = script_dir / 'Pictures'
	default_del_path = script_dir / 'DEL'
	return default_config_path, default_pictures_path, default_del_path


def read_config(config_path):
	try:
		with open(config_path, 'r') as file:
			return json.load(file)
	except FileNotFoundError:
		print(f"Config file not found: {config_path}")
		raise
	except json.JSONDecodeError:
		print(f"Invalid JSON in config file: {config_path}")
		raise


def settings(config):
	picam2 = None
	try:
		picam2 = Picamera2()
		_, default_pictures_path, default_del_path = get_base_paths()
		
		nrphotos = config.get("nrphotos", 10)
		cam_number = config.get("cam_number", "00")
		end_time = config.get("end_time", "06:00")
		quality = config.get("quality", 95)
		camera_w = config.get("camera_w", 4056)
		camera_h = config.get("camera_h", 3040)
		file_path = Path(config.get("file_path", str(default_pictures_path)))
		DEL_path = Path(config.get("DEL_path", str(default_del_path)))
		loop_time = config.get("loop_time", 1)
		noise_threshold = config.get("noise_threshold", 4)
		contour_area_threshold = config.get("contour_area_threshold", 50)
		min_change_percentage = config.get("min_change_percentage", 0.1)
		max_change_percentage = config.get("max_change_percentage", 50)
		
		today_date = datetime.now().strftime("%Y-%m-%d")
		pictures_path = file_path / today_date
		del_path = DEL_path / today_date
		pictures_path.mkdir(parents=True, exist_ok=True)
		del_path.mkdir(parents=True, exist_ok=True)
		
		resolution = picam2.create_still_configuration({"size": (camera_w, camera_h)})
		picam2.configure(resolution)
		picam2.options["quality"] = quality
		picam2.start()
		time.sleep(2)
		
		return picam2, cam_number, pictures_path, del_path, end_time, nrphotos, loop_time, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage
	except Exception as e:
		print(f"Error initializing camera: {str(e)}")
		if picam2:
			picam2.close()
		raise


def capture_and_queue(config, raw_image_queue):
	picam2 = None
	try:
		picam2, cam_number, pictures_path, del_path, end_time, nrphotos, loop_time, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage = settings(
			config)
		
		pic_number = 0
		
		while datetime.now().strftime("%H:%M") != end_time: #and i <= nrphotos: # pay attention to the location of the colon
			loop_start = time.time()
			picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
			current_image = picam2.capture_array()
			raw_image_queue.put((current_image, cam_number, pic_number, pictures_path, del_path, noise_threshold,
								 contour_area_threshold, min_change_percentage, max_change_percentage))
			pic_number += 1
			time_elapsed = time.time() - loop_start
			if time_elapsed < loop_time:
				time.sleep(loop_time - time_elapsed)
	except Exception as e:
		print(f"Error in capture_and_queue: {str(e)}")
	finally:
		if picam2:
			picam2.stop()
			picam2.close()
		raw_image_queue.put(None)


def compare_images(prev_image, current_image, noise_threshold, contour_area_threshold):
	# Convert to grayscale
	prev_gray = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
	curr_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
	
	# Compute absolute difference
	diff = cv2.absdiff(prev_gray, curr_gray)
	
	# Apply noise filter
	noise_mask = diff <= noise_threshold
	filtered_diff = diff.copy()
	filtered_diff[noise_mask] = 0
	
	# Find contours on the filtered difference image
	contours, _ = cv2.findContours(filtered_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	
	# Filter contours by area and calculate total change area
	significant_contours = [c for c in contours if cv2.contourArea(c) > contour_area_threshold]
	total_change_area = sum(cv2.contourArea(c) for c in significant_contours)
	
	# Calculate the change percentage
	total_pixels = curr_gray.shape[0] * curr_gray.shape[1]
	change_percentage = (total_change_area / total_pixels) * 100  # Convert to percentage
	
	return change_percentage, len(significant_contours), significant_contours

def save_image(processed_image_queue):
	picture_number = 1
	while True:
		try:
			image_data = processed_image_queue.get()
			if image_data is None:
				break
			current_image, cam_number, _, should_save, pictures_path, del_path = image_data
			
			timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
			filename = f"cam{cam_number}_{timestamp}_{picture_number:05d}.jpg"
			
			RGB = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
			if should_save:
				save_path = pictures_path / filename
				cv2.imwrite(str(save_path), RGB)
				print(f"  Result: Kept {filename} in original directory")
			else:
				del_save_path = del_path / filename
				cv2.imwrite(str(del_save_path), RGB)
				print(f"  Result: Moved {filename} to DEL directory")
			
			picture_number += 1
			print(f"Queue size: {processed_image_queue.qsize()}")
		except Empty:
			print("Timeout waiting for image in save_image function")


def compare_and_queue(raw_image_queue, processed_image_queue):
	prev_image = None
	while True:
		image_data = raw_image_queue.get()
		if image_data is None:
			break
		
		current_image, cam_number, pic_number, pictures_path, del_path, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage = image_data
		
		if prev_image is not None:
			change_percentage, num_contours, contours = compare_images(prev_image, current_image, noise_threshold,
																	   contour_area_threshold)
			# Determine whether to save or delete the image based on change percentage
			should_save = change_percentage > min_change_percentage
			
			processed_image_queue.put((current_image, cam_number, pic_number, should_save, pictures_path, del_path))
		
		prev_image = current_image


def main():
	try:
		config_path, _, _ = get_base_paths()
		config = read_config(config_path)
		
		raw_image_queue = mp.Queue(maxsize=50)
		processed_image_queue = mp.Queue(maxsize=50)
		
		capture_process = mp.Process(target=capture_and_queue, args=(config, raw_image_queue))
		compare_process = mp.Process(target=compare_and_queue, args=(raw_image_queue, processed_image_queue))
		save_process = mp.Process(target=save_image, args=(processed_image_queue,))
		
		capture_process.start()
		compare_process.start()
		save_process.start()
		
		capture_process.join()
		compare_process.join()
		save_process.join()
	except Exception as e:
		print(f"Error in main function: {str(e)}")


if __name__ == "__main__":
	main()
