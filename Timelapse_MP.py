#!/usr/bin/python3
import time
import json
import cv2
import os
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

def read_config(file_path):
	try:
		with open(file_path, 'r') as file:
			return json.load(file)
	except FileNotFoundError:
		print(f"Config file not found: {file_path}")
		raise
	except json.JSONDecodeError:
		print(f"Invalid JSON in config file: {file_path}")
		raise
def settings(config):
	picam2 = None
	try:
		picam2 = Picamera2()
		nrphotos = config.get("nrphotos", 10)
		cam_number = config.get("cam_number", "00")
		end_time = config.get("end_time", "06:00")
		quality = config.get("quality", 95)
		camera_w = config.get("camera_w", 4056)
		camera_h = config.get("camera_h", 3040)
		file_path = config.get("file_path", '/home/camera/Mothcam/Pictures')
		DEL_path = config.get("DEL_path",'/home/camera/Mothcam/DEL')
		dir_path = config.get("dir_path", '/home/camera/Mothcam')
		similarity = config.get("similarity_percentage", 99) / 100
		loop_time = config.get("loop_time", 1)
		today_date = datetime.now().strftime("%Y-%m-%d")
		resolution = picam2.create_still_configuration({"size": (camera_w, camera_h)})
		picam2.configure(resolution)
		picam2.options["quality"] = quality

		picam2.start()
		time.sleep(2)

		save_pic = os.makedirs(os.path.join(file_path, today_date) exist_ok=True)
		save_del = os.makedirs(os.path.join(DEL_path, today_date), exist_ok=True)
				     
		return picam2, cam_number, file_path, end_time, similarity, nrphotos, loop_time, save_pic, save_del
	except Exception as e:
		print(f"Error initializing camera: {str(e)}")
		if picam2:
			picam2.close()
		raise

def capture_and_queue(config, raw_image_queue):
	picam2 = None
	try:
		picam2, cam_number, file_path, end_time, similarity, nrphotos, loop_time, save_pic, save_del, = settings(config)

		i = 0
		
		while datetime.now().strftime("%H:%M") != end_time and i <= nrphotos:
			loop_start = time.time()
			picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})

			current_image = picam2.capture_array()
			raw_image_queue.put((current_image, cam_number, i))
			i += 1
			print(f"Captured image {i} at {time.strftime('%S')}. Queue size: {raw_image_queue.qsize()}")

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

def compare(raw_image_queue, processed_image_queue, similarity):
	prev_image = None
	while True:
		try:
			image_data = raw_image_queue.get()
			if image_data is None:
				processed_image_queue.put(None)
				break
				
			current_image, cam_number,  i = image_data
			should_save = True

			if prev_image is not None:
				gray1 = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
				gray2 = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
				diff = cv2.absdiff(gray1, gray2)
				diff_percentage = np.count_nonzero(diff) / diff.size

				if diff_percentage <= (1 - similarity):
					    should_save = False

				processed_image_queue.put((current_image, cam_number, i, should_save))

			if should_save:
				prev_image = current_image

			print(f"Compared {i} to previous image. Queue size: {processed_image_queue.qsize()}")

		except Empty:
			print("Timeout waiting for image in compare function")


def save_image(processed_image_queue, save_pic, save_del):
	while True:
		try:
			image_data = processed_image_queue.get()
			if image_data is None:
				break

			current_image, cam_number, i, should_save = image_data
			date_str = datetime.now().strftime("%Y-%m-%d")
			time_str = datetime.now().strftime("%H:%M:%S")

			if should_save:
				# time.sleep(6)
				RGB = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
				cv2.imwrite(f"{'save_pic'}/cam{cam_number}_{date_str}_{time_str}_{i:05}.jpg", RGB)
				print(f"Image {i} saved at {time.strftime('%S')}")
			else:
				RGB = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)
				cv2.imwrite(f"{'save_del'}/cam{cam_number}_{date_str}_{time_str}_{i:05}.jpg", RGB)
				print(f"Image {i} too similar. Saved in DEL at {time.strftime('%S')}")
				print(f"Queue size: {processed_image_queue.qsize()}")
		except Empty:
			print("Timeout waiting for image in save_image function")

def main():
	try:
		config = read_config('/home/camera/Mothcam/mothconfig.json')

		raw_image_queue = mp.Queue(maxsize=50)
		processed_image_queue = mp.Queue(maxsize=50)

		capture_process = mp.Process(target=capture_and_queue, args=(config, raw_image_queue))
		compare_process = mp.Process(target=compare, args=(raw_image_queue, processed_image_queue, config['similarity_percentage'] / 100))
		save_process = mp.Process(target=save_image, args=(processed_image_queue, save_pic, save_del))

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

