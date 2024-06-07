#!/usr/bin/python3
import time

from picamera2 import Picamera2
from libcamera import controls

# Set variables and camera configuration
date = time.strft
picam2 = Picamera2()
config = picam2.create_still_configuration({"size":(4056, 3040)})
picam2.configure(config)
picam2.options["quality"] = 95
picam2.start()

# Give time for Aec and Awb to settle, before disabling them
time.sleep(1)
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous,"FrameRate": 1.0})

# And wait for those settings to take effect
time.sleep(2)
# Loop starts here
start_time = time.time()
    # set number of pictures
for i in range(1, 2):
    # save location and name
    file_path = '/home/Camera/Pictures'
    r = picam2.capture_request(file_path)
    r.save("main", f"Cam1{date}{i}.jpg")
    r.release()
    print(f"Captured image {i} of 50 at {time.time() - start_time:.2f}s")
    time.sleep(5)

picam2.stop()
