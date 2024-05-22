import time
from picamera2 import Picamera2
from libcamera import controls

picam2 = Picamera2()

config = picam2.create_still_configuration({"size":(300, 300)})
picam2.configure(config)
picam2.start()
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous,"FrameRate": 1.0})
time.sleep(15)

metadata = picam2.capture_file("Color_test_Picam.jpg")
print("woohoo!")

picam2.close()








