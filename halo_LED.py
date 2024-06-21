import RPi.GPIO as GPIO

import time
from picamera2 import Picamera2

picam2 = Picamera2()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

GPIO.output(7, GPIO.HIGH)
with picam2 as camera:

        picam2.start()
        time.sleep(3)
        camera.capture_file('/home/camera/test.jpg')
        print("okay lesgo")
        picam2.close()

GPIO.output(7, GPIO.LOW)
