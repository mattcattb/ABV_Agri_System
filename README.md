# ABV Agriculture Capture System

A Jetson Nano camera service for field image capture in agricultural research environments.

![ABV agriculture capture hardware mounted in the field](docs/images/abv-camera-system.jpg)

## About

ABV Agriculture Capture System controls a camera and hardware switches on a Jetson Nano so strawberry field images can be captured consistently during equipment operation. It was developed in collaboration with the UF College of Agriculture and Life Sciences.

## Tech Stack

- Python
- OpenCV
- NanoCamera
- Jetson GPIO
- Linux systemd services
- Bash
- Jetson Nano

## Features

- Startup service for launching the capture workflow automatically.
- Physical switch control for starting and stopping collection.
- RGB status lights for ready, capture, inference, and blocking states.
- 30 FPS image capture to external storage.
- USB mount helper scripts for field storage devices.
- Test scripts for capture and storage behavior.

## My Role

I built the Jetson service workflow, hardware control scripts, capture process, storage handling, and setup scripts needed to deploy the system on the device.

## Hardware Requirements

- Jetson Nano running JetPack SDK
- USB camera
- External USB storage
- RGB status lights
- Two physical switches

## Setup

Install the Jetson dependencies, then run the service setup scripts:

```bash
chmod +x setup_services.sh
chmod +x start_main_script.sh
chmod +x usb_mount.sh
./setup_services.sh
```

After setup, reboot the Jetson or reconnect the USB storage. The green status light indicates that the system is ready.

## Operating Notes

- Start with both switches off.
- Do not remove the active USB storage device while the system is running.
- Blue status indicates active data collection.
- Red status indicates inference mode.
- Blinking red or blue indicates blocking mode; toggle both switches off to exit.

## Future Improvements

- GPS metadata support.
- Stronger structured logging.
- Clearer systemd dependency ordering.
- More complete automated test workflow.
