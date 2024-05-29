from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from libcamera import controls, Transform
import time

picam2 = Picamera2()
camera_config = picam2.create_video_configuration(
    main={"size": (1920, 1080)},
    transform=Transform(hflip=True, vflip=True),
)
picam2.configure(camera_config)
picam2.start(show_preview=False)
picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
encoder = H264Encoder()
picam2.start_recording(encoder, 'test.h264', quality=Quality.VERY_HIGH)
time.sleep(5)
picam2.stop_recording()
