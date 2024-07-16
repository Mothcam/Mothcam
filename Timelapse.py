#!/usr/bin/python3

#import required modules
import time
import RPi.GPIO as GPIO
import json
import cv2
import numpy as np
import os
import multiprocessing as mp

from picamera2 import Picamera2
from libcamera import controls
from datetime import datetime
from queue import Empty

def to_bool(value):
        if str(value).lower() in ("yes", "y", "true",  "t", "1"):
                return True
        elif str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
                return False
        raise ValueError (f"Invalid boolean value: {value}")

def read_config(file_path):
        with open(file_path, 'r') as file:
                config = json.load(file)
        return config

def settings(config):
        picam2 = Picamera2()

        nrfotos =  config.get("nrfotos", 10)
        cam_number = config.get("cam_number", "00")
        end_time = config.get("end_time", "06:00")
        autofocus = to_bool(config.get("autofocus",1))
        focus_dist_m = config.get("focus_dist_m",0.1)
        GPIO_pin = config.get("GPIO_pin",7)
        quality = config.get("quality",95)
        camera_w = config.get("camera_w", 4056)
        camera_h = config.get("camera_h", 3040)
        file_path = config.get("file_path", '/home/camera/Mothcam/Pictures')
        date_format = config.get("date", "%Y%m%d")
        date = time.strftime(date_format)
        accuracy = config.get("similarity_percentage", 99)/ 100
        loop_time = config.get("loop_time", 1)
        resolution = picam2.create_still_configuration({"size": (camera_w, camera_h)})
        picam2.configure(resolution)
        picam2.options["quality"] = quality


        if autofocus:
                picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
        else:
                focus_dist = 1 / focus_dist_m if focus_dist_m > 0 else 1
                picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": focus_dist})


        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_pin, GPIO.OUT)

        picam2.start()
        time.sleep(2)
        return  picam2, cam_number, file_path, date, GPIO_pin, end_time, accuracy, nrfotos, loop_time, autofocus

def compare(prev_image, current_image, accuracy):
        gray1 = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(current_image, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray1, gray2)
        diff_percentage = np.count_nonzero(diff) / diff.size
        return diff_percentage <= (1 - accuracy)

def save_image(file_path, current_image, prev_image, accuracy, cam_number, date, i):

        if prev_image is not None and compare(prev_image, current_image, accuracy):
                cv2.imwrite(f"{'/home/camera/Mothcam/DEL'}/cam{cam_number}-{date}-{i:05}.jpg", current_image)
                print(f"image{i} too similar. Saved in DEL at {time.strftime('%S')}")
                return False, None

        else:
                cv2.imwrite(f"{file_path}/cam{cam_number}-{date}-{i:05}.jpg", current_image)
                print(time.strftime("%S"))
                return True, current_image

def main():
        config_file = '/home/camera/Mothcam/mothconfig.json'
        config = read_config(config_file)
        picam2, cam_number, file_path, date, GPIO_pin, end_time, accuracy,nrfotos, loop_time, autofocus = settings(config)
        os.makedirs(file_path, exist_ok = True)
        os.makedirs(os.path.join(file_path, 'DEL'), exist_ok = True)

        prev_image = None
        i = 1

        while datetime.now().strftime("%H:%M") != end_time or i <= nrfotos:
                loop_start = time.time()

                GPIO.output(GPIO_pin, 1)
                current_image = picam2.capture_array()
                saved, new_prev_image = save_image(file_path, current_image, prev_image, accuracy, cam_number, date, i)

                if saved:
                        prev_image = new_prev_image
#               GPIO.output(GPIO_pin, 0)

                i = i + 1
                time_elapsed = time.time() - loop_start
                if time_elapsed < loop_time:
                        time.sleep(loop_time - time_elapsed)

        picam2.stop()
        GPIO.cleanup()

if __name__== "__main__":
        main()
