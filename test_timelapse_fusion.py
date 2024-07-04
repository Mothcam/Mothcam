#!/usr/bin/python3
#import required modules
import time
import RPi.GPIO as GPIO
import json, sys, os.path, pathlib

from picamera2 import Picamera2
from libcamera import controls

picam2 = Picamera2()

def to_bool(value):
        if str(value).lower() in ("yes" "y" "true"  "t" "1"):
                return True
        elif str(value).lower() in ("no"  "n" "false" "f" "0" "0.0" "" "none" "[]" "{}"):
                return False

        print("Issue with settings value:", value)

def config():
        with open('mothconfig.json', 'r') as file:
                settings = json.load(file)



        # Autofocus logic
        autofocus = settings['autofocus'] == '01'
        if autofocus:
                controls = {"AfMode": 1}  # Assuming 1 is the value for autofocus in your library
        else:
                focus_dist_m = float(settings['focus_dist_m'])
                focus_dist = 1 / focus_dist_m if focus_dist_m > 0 else 10
                controls = {"AfMode": 0, "LensPosition": focus_dist}
        # Configure camera settings
        camera_config = picam2.create_still_configuration(main={"size": (int(settings['camera_w']), int(settings['camera_h']))})
        picam2.configure(camera_config)

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(int(settings['GPIO_pin']), GPIO.OUT)

        return settings

def main(settings):
        setting = config()
for i in range(1,int(settings['nrfotos'])+ 1):
#       #Flash on
        GPIO.output(int(settings['GPIO_pin']),1)
#       #Make pictures
        picture = picam2.capture_file(seetings['file_path'])
#       #set filename as
        picture.save("main", f"{settings['file_path']}/cam{settings['cam_number']}-{settings['date']}-{i:05}.jpg")
#       #Turn light off again (0 = OFF)
        GPIO.output(int(settings['GPIO_pin']),0)
        r.release()
        print ("pic taken")
        time.sleep(1)

#def config():
#    with open('mothconfig.json', 'r') as file:
#        settings = json.load(file)
#    return settings

#def main():
#       settings = config()

##auto focus settings
#       if autofocus:
#               controls = {"AfMode": 1}
#       else:
#               focus_dist_m = float(settings['focus_dist_m'])
#               focus_dist = 1 / focus_dist_m if focus_dist_m > 0 else 10
#               controls = {"AfMode": 0, "LensPosition": focus_dist}
##Configure camera settings
#       camera_config = picam2.create_still_configuration(
#               main={"size": (int(settings['camera_w']), int(settings['camera_h']))})

#       picam2.configure(camera_config)
#       GPIO.setmode(GPIO.BOARD)
#       GPIO.setup(GPIO_pin, GPIO.OUT)


#       picam2.start()
#       time.sleep(1)
#       start_time = time.time()

#for i in range(1, nrfotos + 1):
#       #Flash
#       GPIO.output(GPIO_pin,1)
#       #Make pictures
#       picture = picam2.capture_request(file_path)
#       #set filename as
#       picture.save("main", f"{file_path}/cam{cam_number}-{date}-{i:05}.jpg")
#       #Turn light off again (0 = OFF)
#       GPIO.output(GPIO_pin,0)
#       r.release()
#       print ("pic taken")
#       time.sleep(1)
#picam2.stop()
if __name__== "__main__":
        main()

