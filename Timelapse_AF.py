#!/usr/bin/python3
#import required modules
import time
import RPi.GPIO as GPIO
import json
import sys

from picamera2 import Picamera2
from libcamera import controls


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
        picam2 = Picamera2()
        config_file = '/home/camera/Mothcam/mothconfig.json'
        config = read_config(config_file)

        #get the settings from the config file
        nrfotos = config.get("nrfotos", 3)
        cam_number = config.get("cam_number",0)
        start_hhmm = config.get("start_hhmm", "22 00")
        end_hhmm = config.get("end_hhmm", "06 00")
        autofocus = config.get("autofocus",0)
        focus_dist_m = config.get("focus_dist_m", 0.1)
        GPIO_pin = config.get("GPIO_pin",7)
        quality = config.get("quality",95)
        camera_w = config.get("camera_w", 4056)
        camera_h = config.get("camera_w",3040)
        file_path = config.get("file_path", '/home/camera/Mothcam/Pictures')
        colour_space = config.get("colour")
        date = config.get("date", "%Y%m%d")
	        date = time.strftime(date)


        config = picam2.create_still_configuration({"size": (camera_w, camera_h)})
        picam2.configure(config)
        picam2.options["quality"]= quality
        time.sleep(1)
        #auto focus settings
        if autofocus:
                picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
        else:
                focus_dist = 1 / focus_dist_m if focus_dist_m > 0 else 1
                picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": focus_dist})
        #set up GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIO_pin, GPIO.OUT)
        picam2.configure(config)
        picam2.start()
        time.sleep(1)

        for i in range(1, nrfotos + 1):
                #Flash
                GPIO.output(GPIO_pin, 1)
                print("ON")
                #Make pictures
                r = picam2.capture_request(file_path)
                print("R")
                #set filename as
                r.save("main", f"{file_path}/cam{cam_number}-{date}-{i:05}.jpg")
                print(time.strftime("%S"))
                #Turn light off again (LOW=off)
                GPIO.output(GPIO_pin, 0)
                print("OFF")
                r.release()
                time.sleep(0.1)

        picam2.stop()
if __name__== "__main__":
        main()
