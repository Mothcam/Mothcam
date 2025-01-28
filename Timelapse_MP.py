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

#to_bool turns all binairy values to either 1 or 0
def to_bool(value):
	if isinstance(value, bool):
		return value
	if str(value).lower() in ("yes", "y", "true", "t", "1"):
		return True
	if str(value).lower() in ("no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
		return False
	raise ValueError(f"Invalid boolean value: {value}")

#Find the location of the folder where to script is located, necessary for creating the folders where the photographs will be stored.
def get_base_paths():
	script_dir = Path(__file__).parent.resolve()
	default_config_path = script_dir / 'mothconfig.json'
	default_pictures_path = script_dir / 'Pictures'
	default_del_path = script_dir / 'DEL'
	return default_config_path, default_pictures_path, default_del_path

#Find the location of the the config file, this is needed to later get the preferred settings.
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

#All settings can be found here
def settings(config):
	picam2 = None
	try:
		picam2 = Picamera2()
		_, default_pictures_path, default_del_path = get_base_paths()
#Importing the settings which can be set in the config file		
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
		stop_method = config.get("stop_method", "time")
		save_all_images = to_bool(config.get("save_all_images", True))
#Get the time and create a new folder with todays date		
		today_date = datetime.now().strftime("%Y-%m-%d")
		pictures_path = file_path / today_date		
		del_path = DEL_path / today_date
#Create the save locations for the images
		if save_all_images is False:
			pictures_path.mkdir(parents=True, exist_ok=True)
		else:
			pictures_path.mkdir(parents=True, exist_ok=True)
			del_path.mkdir(parents=True, exist_ok=True)
#Tell the camera what settings to use		
		resolution = picam2.create_still_configuration({"size": (camera_w, camera_h)})
		picam2.configure(resolution)
		picam2.options["quality"] = quality
		picam2.start()
		time.sleep(2)
		
		return picam2, cam_number, pictures_path, del_path, end_time, nrphotos, loop_time, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage, stop_method, save_all_images
	except Exception as e:
		print(f"Error initializing camera: {str(e)}")
		if picam2:
			picam2.close()
		raise

#This function takes a picture and forwards it to the process where empty images are filtered
def capture_and_queue(config, raw_image_queue):
	picam2 = None
#This part is required for the script to know what is said in the config file	
	try:
		picam2, cam_number, pictures_path, del_path, end_time, nrphotos, loop_time, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage, stop_method, save_all_images = settings(config)
		
		pic_number = 0
#"While True:" starts a loop, which end depending on what the settings are set to. It can end on a time, on a specific number of photo's taken or depending on which on is reached first
		while True:
			if stop_method == "end_time" and datetime.now().strftime("%H:%M") == end_time:
				break
			elif stop_method == "nrphotos" and pic_number >= nrphotos:
				break
			elif stop_method == "either" and (datetime.now().strftime("%H:%M") == end_time and pic_number >= nrphotos):
				break
			
			loop_start = time.time()
#Focus			
			picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
#Take picture			
			current_image = picam2.capture_array()
#Put the picture in a queue to be compared. If the queue is not used, the script will get itself stuck here.
			raw_image_queue.put((current_image, cam_number, pic_number, pictures_path, del_path, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage, save_all_images))
#increase the image number by 1 for the next image, the order has to stay 
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
		
# Compare consecutive images to detect changes between them and puts it in a queue to be saved depending on the difference
def compare_images(raw_image_queue, processed_image_queue):
  # Since we need two images to detect changes, First image is stored as reference only - no comparison needed
	prev_image = None
	while True:
		image_data = raw_image_queue.get()
		if image_data is None:
			processed_image_queue.put(None)
			break
		
		current_image, cam_number, pic_number, pictures_path, del_path, noise_threshold, contour_area_threshold, min_change_percentage, max_change_percentage, save_all_images = image_data
 # Process images only when we have a previous image to compare against		
		if prev_image is not None:
			  # Convert images to grayscale to simplify change detection, Grayscale values range from 0 (black) to 255 (white)
			prev_gray = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
			curr_gray = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
			
			 # Calculate pixel-by-pixel absolute difference between images to identify changed areas
			diff = cv2.absdiff(prev_gray, curr_gray)
			
			# Apply noise threshold to eliminate minor variations. Pixels with differences below threshold are set to 0
			noise_mask = diff <= noise_threshold
			filtered_diff = diff.copy()
			filtered_diff[noise_mask] = 0
			
			# Identify connected regions of change using contour detection.
			## A contour is a curve joining continuous points having the same intensity
			contours, _ = cv2.findContours(filtered_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			
			# Filter contours by comparing their area (in pixels) against contour_area_threshold
			## A "significant" contour is one larger than contour_area_threshold, which helps ignore small changes like shadows or camera noise. Then sum up the total area of all significant contours
			significant_contours = [c for c in contours if cv2.contourArea(c) > contour_area_threshold] 
			total_change_area = sum(cv2.contourArea(c) for c in significant_contours)
			
			 # Convert total change area to a percentage of the image, to determine if enough change occurred to save the image
			total_pixels = curr_gray.shape[0] * curr_gray.shape[1]
			change_percentage = (total_change_area / total_pixels) * 100
			
			# Determine whether to save or delete the image based on change percentage
			should_save = change_percentage > min_change_percentage
			#Put the image in the queue to be saved or to be deleted
			processed_image_queue.put(
				(current_image, cam_number, pic_number, should_save, pictures_path, del_path, save_all_images))
		
		prev_image = current_image

#This function handles the saving process
def save_image(processed_image_queue):
	picture_number = 1
	while True:
		try:
			#do nothing if there is no image or if it is image 0
			image_data = processed_image_queue.get()
			if image_data is None:
				break
			current_image, cam_number, _, should_save, pictures_path, del_path, save_all_images = image_data
			#retrieve time and date, which will be used for the filename
			timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
			# This line decides the file name.
			filename = f"cam{cam_number}_{timestamp}_{picture_number:05d}.jpg"
			#The picture is taken with Blue Green Red, but will be displayed as Red Green Blue. This line formats the colour coding to the correct format. 
			#Without this line the images will turn Green and Orange.
			RGB = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
			#If the config was set to save_all images
			if save_all_images:
				#if the compare function found a significant difference, save the photgraph in the save folder
				if should_save:
					save_path = pictures_path / filename
					cv2.imwrite(str(save_path), RGB)
				#if the compare function did not find a significant difference, save the photograph in a seperate folder
				else:
					del_save_path = del_path / filename
					cv2.imwrite(str(del_save_path), RGB)
			#If the config is not set to save_all_images:		
			else:
				#If the compare function found a significant difference, save the photograph in the save folder
				if should_save:
					save_path = pictures_path / filename
					cv2.imwrite(str(save_path), RGB)
				#If the compare function did not find a significant difference, it will discard the image
				else:
					print(f"  Result: Discarded {filename} due to similarity")
			
			picture_number += 1
			print(f"Queue size: {processed_image_queue.qsize()}")
		except Empty:
			print("Timeout waiting for image in save_image function")
#The pi will view this as the main part of the script. This function initate the multiprocessing of all the former functions.
#Multipprocessing (MP) allows the pi to take photographs once per second instead of takes 5-10 seconds. 
def main():
	try:
		config_path, _, _ = get_base_paths()
		config = read_config(config_path)
		#Sets a limit for the queue size. The queue will not go above 2 in this version of the script. If the queue limit is reached the script is paused untill the queue is at 49 again
		raw_image_queue = mp.Queue(maxsize=50)
		processed_image_queue = mp.Queue(maxsize=50)
		#states which functions should me multiprocessed
		capture_process = mp.Process(target=capture_and_queue, args=(config, raw_image_queue))
		compare_process = mp.Process(target=compare_images, args=(raw_image_queue, processed_image_queue))
		save_process = mp.Process(target=save_image, args=(processed_image_queue,))
		#start the different functions
		capture_process.start()
		compare_process.start()
		save_process.start()
		
		capture_process.join()
		compare_process.join()
		save_process.join()
	except Exception as e:
		print(f"Error in main function: {str(e)}")

#without this the script will not work. 
if __name__ == "__main__":
	main()
