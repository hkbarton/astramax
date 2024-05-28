import pyaudio
import time
import queue
import numpy as np
import threading
from typing import TypedDict
from google.cloud import speech

# Audio recording parameters
RATE = 44100
CHUNK = int(RATE / 10)  # 100ms
DEVICE_INDEX = 1


class RecorderSignals(TypedDict):
    triggered: threading.Event
    finished: threading.Event


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk, silence_threshold=500, stop_after=None):
        self._rate = rate
        self._chunk = chunk
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self._closed = True
        self._silence_threshold = silence_threshold
        self._silence_start_time = None
        self._stop_after = stop_after

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            input_device_index=DEVICE_INDEX,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self._closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self._closed = True
        # Signal the generator to terminate
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        self._check_silence(in_data)
        return None, pyaudio.paContinue

    def _check_silence(self, data):
        audio_data = np.frombuffer(data, dtype=np.int16)
        audio_level = np.abs(audio_data).mean()
        if audio_level < self._silence_threshold:
            if self._silence_start_time is None:
                self._silence_start_time = time.time()
        else:
            self._silence_start_time = None

    def set_stop_after(self, stop_after):
        self._stop_after = stop_after

    def generator(self):
        while not self._closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)
            if self._stop_after and self._silence_start_time and time.time() - self._silence_start_time > self._stop_after:
                break


class SpeechRecorder:
    def __init__(self):
        self.client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
        )
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,
        )
        pass

    def record_after_trigger_word(self, trigger_word, callback, signals: RecorderSignals):
        recorded_text = ""
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)
            responses = self.client.streaming_recognize(
                self.streaming_config, requests)

            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                if trigger_word.lower() in transcript.lower():
                    signals["triggered"].set()
                    recorded_text = transcript.strip()
                    stream.set_stop_after(2)
        callback(recorded_text)
        signals["finished"].set()
