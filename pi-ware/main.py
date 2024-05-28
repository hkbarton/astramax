import time
import os
import threading
import queue
from lib import SpeechRecorder, RecorderSignals, generate_unique_uuid
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from libcamera import controls, Transform


def record_after_trigger_word(recorder: SpeechRecorder, signals: RecorderSignals):
    signals["triggered"].clear()
    signals["finished"].clear()
    audio_thread = threading.Thread(
        target=recorder.record_after_trigger_word, args=("hi Gemini", capture_speech, signals,))
    audio_thread.start()
    # capture_video()


def capture_video():
    video_file_name = f'{generate_unique_uuid()}.h264'
    encoder = H264Encoder()
    picam2.start_recording(
        encoder, video_file_name, quality=Quality.VERY_HIGH)
    time.sleep(3)
    picam2.stop_recording()
    recorded_video_file.put(video_file_name)


def capture_speech(text):
    recorded_text.put(text)


def process_recording():
    prompt = recorded_text.get()
    video_file = recorded_video_file.get()
    print("========================")
    print("========================")
    print("========================")
    print(prompt)
    print("\n")
    print(video_file)
    print("========================")
    print("========================")
    print("========================")


if __name__ == "__main__":
    recorded_text = queue.Queue()
    recorded_video_file = queue.Queue()
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
    signals: RecorderSignals = {
        "triggered": threading.Event(),
        "finished": threading.Event()
    }
    while True:
        record_after_trigger_word(recorder, signals)
        signals["triggered"].wait()
        capture_video()
        signals["finished"].wait()
        process_recording()
