#!/usr/bin/python3
#import required modules
import time
import json
import sys

from picamera2 import Picamera2
from libcamera import controls
#Read the config file
def read_config(file_path):
	print("File_path:", file_path)
	try:
		with open(file_path, 'r') as file:
			config =json.load(file)
	except FileNotFoundError:
		print(f"Error: The file {file_path} was not found")
		sys.exit(1)
	except json.JSONDecodeError:
		print(f":Error: The {file_path} is not a valid JSON file")
		sys.exit(1)
	except Exception as e:
		print(f"Error reading config file: {e}")
		sys.exit(1)
	return config


def main():
	# Take the number of photo's out of the config file. When failed 3 pictures will be taken
	config_file = '/home/camera/Mothcam/mothconfig.json'
	config = read_config(config_file)
	nrfotos = config.get("nrfotos", 3)
	# Take the camera number out of the config file. When failed the number will be 00
	file_path = config.get("file_path",'/home/camera/Mothcam/Pictures')
	cam_number = config.get("cam_number","00")
	
#Set variables
	date = time.strftime("%Y%m%d")
	picam2 = Picamera2()
	config = picam2.create_still_configuration({"size":(4056, 3040)})
	picam2.configure(config)
	picam2.options["quality"] = 95
	picam2.start()


	# Give time for Aec and Awb to settle, before disabling them and wait for those settings to take effect
	time.sleep(1)
	picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous,"FrameRate": 1.0})

	#Instructions to the Picamera to take pictures
	time.sleep(2)
	start_time = time.time()

	for i in range(1, nrfotos + 1):
		r = picam2.capture_request(file_path)
		#set filename as
		r.save("main", f"{file_path}/cam{cam_number}-{date}-{i:05}.jpg")
		r.release()
		time.sleep(1)

	picam2.stop()

if __name__== "__main__":
        main()
