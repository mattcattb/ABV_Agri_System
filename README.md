# ABV Camera Monitoring System

This project provides stable control over a camera monitoring system for agriculture field capture use. This project was developed in colaboration with the UF College of Agriculture and Life Sciences. 

![ABV attached to pesticide sprayer](IMG_9503.jpg)

## Project Overview

This system includes one core functionality:
- **Data Collection Switch**: Activates and saves images at 30 FPS to external storage when toggled.

The system is made to be as dynamic as possible, being able to withstand any system thrown at it.

## Control Flow

1. **Startup**: 
   - Plug in only one USB (SDA) before starting. Do not remove this while the system is on.
   - The green light will blink during startup. When it turns solid green, the system is ready.

2. **Blocking Mode**: 
   - If the red or blue lights are blinking, the system is in blocking mode. Toggle both switches off to exit.
   - **Green**: Main system running  
   - **Blue**: Data collection active (storing images)  
   - **Red**: YOLO model making inferences  

3. **Switches**:  
   - **L_Switch**: Begin data collection  
   - **R_Switch**: Begin inferencing 

4. **Usage**: 
   - Start with both switches off. Do not activate both switches simultaneously, as this will cause blocking mode.

5. **Data Collection**: 
   - Data collection takes pictures at 30 FPS and stores them in one of the run folders.

6. **Inferencing**: 
   - Inferencing mode starts running the YOLOv8 model on all of the pictures taken and stored from data collection. Do not run before data collection is done.

7. **Shutdown**: 
   - Turn off the system and then unplug the USB.

## Requirements

### Hardware
- Jetson Nano (Jetpack SDK)
- USB Camera
- RGB lights (Red, Blue, Green)
- 2 Switches

### Software
- OpenCV (cv2)
- Archiconda
- Nanocamera
- Python 3.8
- Python services
- python3-jetson-gpio
- exFAT (install via `sudo apt-get install exfat-fuse exfat-utils`)

### Setup

1. **Download and Setup Conda Environment**:
   - Create environment and install NanoCamera, OpenCV, and Jetson GPIO libraries.

2. **Setup Services**:
   ```sh
   chmod +x setup_services.sh
   chmod +x start_main_script.sh
   chmod +x usb_mount.sh
   ./setup_services.sh
   ```
   This will copy all services to the services section and enable them.

3. **Run Software**:
   - Your setup is now complete! Reboot your Jetson or unplug and replug the USB to see the light start blinking.


### Future Goals

- Add GPS Support
- USB Device Connection
- Add stronger logging
- Add service dependencies
- Finish Test Workflow