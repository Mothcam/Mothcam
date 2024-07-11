#!/usr/bin/python3
#import required modules
import time
import RPi.GPIO as GPIO
import json
import sys

from picamera2 import Picamera2
from libcamera import controls
from datetime import datetime, timedelta

def to_bool(value):
	""" Converts argument to boolean. Raises exception for invalid formats
        Possible True  values: 1, True, true, "1", "True", "yes", "y", "t"
        Possible False values: 0, False, false, None, [], {}, "", "0", "False", "no", "n", ">
	"""

	if str(value).lower() in ("yes", "y", "true",  "t", "1"): # case lowercase value string >
		return True                                   # True is returned
	elif str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): 
		return False                                  # False is returned
	print("Issue with settings value:", value)      # case if and elif aren't sattisfied
	raise Exception                                   # exception is raised

def read_config(file_path):
	with open(file_path, 'r') as file:
		config =json.load(file)
	return config

def settings(config):
	picam2 = Picamera2()
	nrfotos = config.get("nrfotos, 3")
	cam_number = config.get("cam_number",0)
	end_time = config.get("end_time", "06:00")
	autofocus = config.get("autofocus",1)
	focus_dist_m = config.get("focus_dist_m", 0.1)
	GPIO_pin = config.get("GPIO_pin",7)
	quality = config.get("quality",95)
	camera_w = config.get("camera_w", 4056)
	camera_h = config.get("camera_h",3040)
	file_path = config.get("file_path", '/home/camera/Mothcam/Pictures')
	date = config.get("date", "%Y%m%d")
	date = time.strftime(date)

	resolution = picam2.create_still_configuration({"size": (camera_w, camera_h)})
	picam2.configure(resolution)
	picam2.options["quality"] = quality
	time.sleep(1)

	#auto focus settings
	if autofocus:
		picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
	else:
		focus_dist = 1 / focus_dist_m if focus_dist_m > 0 else 1
		picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": focus_dist})
	# Set up GPIO
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(GPIO_pin, GPIO.OUT)

	picam2.configure(resolution)
	picam2.start()
	time.sleep(1)
	return  picam2, cam_number, file_path, date, GPIO_pin, end_time

def main():
	config_file = '/home/camera/Mothcam/mothconfig.json'
	config = read_config(config_file)
	picam2, cam_number, file_path, date, GPIO_pin, end_time = settings(config)

        #loop to take picture
	#for i in range (1, nrfotos, +1)
	i = 1
	while True:
		if datetime.now().strftime("%H:%M")== end_time:
			break

                #Flash
		GPIO.output(GPIO_pin, 1)
		#Make pictures
		r = picam2.capture_request(file_path)
                #set filename as
		r.save("main", f"{file_path}/cam{cam_number}-{date}-{i:05}.jpg")
		#print(time.strftime("%S"))
		#Turn light off again (LOW=off)
		GPIO.output(GPIO_pin, 0)
		r.release()
		i = i + 1
	picam2.stop()
if __name__== "__main__":
        main()

