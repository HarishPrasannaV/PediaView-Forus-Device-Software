# Forus PediaView Device Software
- Software for the PediaView Device developed for Forus Health
- Pediview is a device developed for screening pediatric children for rential abnormalities and refractive errors using red reflex images of their eyes

## Device Setup:
- Steps that have to be followed before running the PediaView Software:
## Hardware Connections:
- Connect Pi Zero 2W with the PCB hat
- Connect the LED PCB with the PCB hat
- Connect the camera with Pi Zero 2W
- Connect the LCD Display to Pi Zero 2W
- Drivers and Libraries Installation:
- Install the LCD Display driver from: https://github.com/CytronTechnologies/xpt2046-LCD-Driver-for-Raspberry-Pi
- Install OpenCV using: **`sudo apt-get install libopencv-dev python3-opencv`**
- Install Tkinter
- Install Pillow
- Install Picamera2
- Install Pyzbar
- Install RPi.GPIO
- Install Numpy
- Clone the PediView Device software repo

### Running the Program:
Go to the pediaview directory and run **`DISPLAY=:0 python3 main.py`**
# Software Architecture and Program Details:
- The Main GUI and GUI of all other components are built with Tkinter as it is extremely light and can run smoothly with the limited processing power of Raspberry Pi Zero 2W.

## Main GUI:
- The main GUI has “Screening Button”, “Gallery Button” & “Test Capture Button” in that order.
- There is also an extras button at the bottom left which gives access to the QR scan testing feature and test gallery.
- Finally, there is the quit button at the bottom right.
- The main GUI also implements popups which act as loading screen while opening other softwares.


## Galleries:
- The gallery opens images stored in various folders in the name of patient MRN within the captured folder.
- The gallery is for images captured in the screening mode
- The test gallery opens images stored within the test_captured folder
- The test gallery is for images captured in the test capture mode
- User can cycle through the images in folder with provided arrow keys
- The thumbnail which shows the most recently captured images in both screening and test capture mode will also open respective galleries.


## QR Testing:
- The QR test capturing GUI has a main thumbnail in which the live camera feed is displayed
- There is a quit button at the bottom.
- The QR code scanned is expected to be in JSON format and there must be a field called ‘MRN’, if there is no MRN or if the data is not in JSON from the program will throw an error.
- Each frame is scanned for QR code and the live feed is continued until one is detected
- If the scanned QR code is valid, then a popup with the scanned data is displayed and the user can either confirm or reject it.


## Image Capturing:
- The GUI has a thumbnail in which the live feed from the camera will be displayed.
- There is a thumbnail at the bottom right which shows the preview of the most recently captured image, clicking on the preview image will take the user to the test gallery or the gallery depending on which mode the user is in.
- Both the IR LEDs are turned on when the program starts and the pins 21,23 & 27 are set to high to activate various ICs in the PCB(Primarily the digital potentiometer)
- The intensity is set to 0xFF for the IR LEDs and the address of the digipot is 0x2E
- The frames are captured in a separate thread and stored in a frame container
- The frames are then updated in the the thumbnail every(67ms, corresponding to 15FPS) in the GUI for live feed
- The frame capture and displaying is handled separately to ensure smooth preview and optimize performance
- The capture configuration for Picamera 2 with Pi HQ camera is down below:
  - "ExposureTime": 66657
  - "ColourGains": (1.5, 3.0), used to adjust the amount of red and blue in the image
  - "AnalogueGain": 7.5
- When the capture button is triggered, first the IR image is captured and saved. And then the flash led function is called in a separate thread and the red reflex is captured.
- The flash function being called in a separate thread ensures that the captured frame is consistently synced with the LED flash
- The intensity for the white LED is set as 0xBF which corresponds to 75% of the maximum intensity
- The images along with the data is stored and the preview thumbnail is updated




### Test Capture:
- In test capture, the user can directly proceed to image capturing without scanning patient data QR.
- The images will be stored in test_captured folder
### Screening:
- In screening mode, the user has to scan a QR code which contains valid data with MRN after which there will be a popup.
- The software will proceed into capture mode if the user confirms the patient data from QR
- The data from the QR will also be stored in a text file in the folder along with the images in the folder in the name of MRN and within the captured folder

## Additional Software:
Run the python code in the QR Generator folder to generate QRs for scanning
	

