import time
import os
import threading
from lib import SpeechRecorder
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from libcamera import controls, Transform


def on_trigger_word_detected():
    audio_thread = threading.Thread(
        target=recorder.record_until_silence, args=(capture_speech))
    audio_thread.start()
    # capture_video()


def capture_video():
    encoder = H264Encoder()
    picam2.start_recording(encoder, 'test.h264', quality=Quality.VERY_HIGH)
    time.sleep(5)
    picam2.stop_recording()


def capture_speech(text):
    print(text)


if __name__ == "__main__":
    # Set up GCP authentication
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.path.dirname(os.path.abspath(
            __file__)),
        "../deployment/dev/credentials/ghack-service-account.json"
    )
    # init camera
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration(
        main={"size": (1920, 1080)},
        transform=Transform(hflip=True, vflip=True),
    )
    picam2.configure(camera_config)
    picam2.start(show_preview=False)
    picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
    # init audio recorder
    recorder = SpeechRecorder()
    while True:
        recorder.detect_trigger_word("hi Gemini", on_trigger_word_detected)
        time.sleep(1)
