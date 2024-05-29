### Prepare on PI(assuming Python and Pip already installed):

```
// install libcamera, pyaudio and related library
sudo apt install -y python3-libcamera python3-kms++ libcap-dev python3-picamera2
sudo apt install -y python3-prctl libatlas-base-dev ffmpeg libopenjp2-7 python3-pip
sudo apt install -y libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 libatlas-base-dev python3-pyaudio

// install python lib, note we don't use pipenv for pi-ware
pip3 install google-cloud-aiplatform google-cloud-speech google-cloud-storage google-auth dotenv --break-system-packages
```

### Run on PI

```
python main.py
```
