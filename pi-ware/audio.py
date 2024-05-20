import pyaudio
import numpy as np


def get_audio_stream(chunk_size=1024, rate=16000, channels=1):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=channels,
                        rate=rate, input=True, frames_per_buffer=chunk_size)
    return stream


def read_audio_stream(stream, chunk_size=1024):
    data = stream.read(chunk_size)
    audio_data = np.frombuffer(data, dtype=np.int16)
    return audio_data
