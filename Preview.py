import time

from picamera2 import Picamera2, Preview
from libcamera import controls

picam2 = Picamera2()
config = picam2.create_still_configuration({"size":(1920, 1080)})
picam2.configure(config)
picam2.start_preview(Preview.QTGL)

preview_config = picam2.create_preview_configuration()
picam2.configure(preview_config)

picam2.start()
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})
time.sleep(120)


