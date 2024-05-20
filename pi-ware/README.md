### Prepare on PI(assuming Python and Pip already installed):

```
// install libcamera and related library
sudo apt install -y python3-libcamera python3-kms++
sudo apt install -y python3-prctl libatlas-base-dev ffmpeg libopenjp2-7 python3-pip
// install picamera2 seperately, pipenv install picamera2 doesn't work
pip3 install picamera2 --break-system-packages
// install pipenv on PI
pip install --user pipenv --break-system-packages
```

### Run on PI
```
pipenv install
```
