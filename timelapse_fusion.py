  GNU nano 7.2                                                                           Timelapse_AF.py *
#!/usr/bin/python3
#import required modules
import time
import RPi.GPIO as GPIO
import json, sys, os.path, pathlib

from picamera2 import Picamera2
from libcamera import controls

def to_bool(value):
        if str(value).lower() in ("yes" "y" "true"  "t" "1"):
                return True
        elif str(value).lower() in ("no"  "n" "false" "f" "0" "0.0" "" "none" "[]" "{}"):
                return False

        print("Issue with settings value:", value)
        raise Exception

def Set(file_path):
        settings = {}
        with open(file_path, 'r') as file:
                settings = json.load(file)

        settings['GPIO_pin'] = GPIO_pin
        settings['picam2'] = picam2
        settings['end_hhmm'] = end_hhmm
        settings['date']= date
        settings['quality'] = quality
        settings['camera_w'] = camera_w
        settings['camera_h'] = camera_h
        settings['autofocus'] = autofocus
        settings['focus_dist_m'] = focus_dist_m
        settings['config_file '] = config_file  #add pathlib.path().resolve() to config for this variable
        settings['file_path']= file_path
        settings['nrfotos'] = nrfotos

        except: pirnt("error")
        return settings
def main():
        settings = Set(file_path)

picam2 = Picamera2()
config = picam2.create_still_configuration({"size":(settings['camera_w'],settings['camera_h'])})

picam2.configure(config)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIO_pin, GPIO.OUT)

if autofocus:
        picam2.set_controls({"AfMode": controls.AfModeEnum.Auto})
else:
        focus_dist = 1/focus_dist_m if focus_dist_m > 0 else 10
        picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": focus_dist})



picam2.start()
time.sleep(1)
start_time = time.time()

for i in range(1, nrfotos + 1):
        #Flash
        GPIO.output(GPIO_pin,1)
        #Make pictures
        picture = picam2.capture_request(file_path)
        #set filename as
        picture.save("main", f"{file_path}/cam{cam_number}-{date}-{i:05}.jpg")
        #Turn light off again (0 = OFF)
        GPIO.output(GPIO_pin,0)
        r.release()
        print ("pic taken")
        time.sleep(1)

picam2.stop()
if __name__== "__main__":
        main()
