### Prepare on PI(assuming Python and Pip already installed):

```
// install libcamera and related library
sudo apt install -y python3-libcamera python3-kms++ libcap-dev
sudo apt install -y python3-prctl libatlas-base-dev ffmpeg libopenjp2-7 python3-pip

// install portaudio for audio capture
sudo apt-get install libasound-dev
wget https://files.portaudio.com/archives/pa_stable_v190700_20210406.tgz && tar xzf pa_stable_v190700_20210406.tgz && rm -rf pa_stable_v190700_20210406.tgz
./configure
make
sudo make install

// install python lib, note we don't use pipenv for pi-ware
pip3 install picamera2 pyaudio numpy google-cloud-aiplatform --break-system-packages
```

### Run on PI

```
python main.py
```
