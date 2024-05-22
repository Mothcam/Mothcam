import time
from picamera2 import Picamera2
from libcamera import controls

picam2 = Picamera2()
config = picam2.create_still_configuration({"size":(4056, 3040)})
picam2.configure(config)
picam2.options["quality"] = 100
picam2.start()
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})
time.sleep(10)

metadata = picam2.capture_file("quality100_4056x3040_Picam.jpg")
print("Unbeelievable!")

picam2.close()
