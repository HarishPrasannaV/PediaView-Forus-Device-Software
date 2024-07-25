import cv2
from picamera2 import Picamera2
import time
import threading
import RPi.GPIO as GPIO
from tkinter import Tk, Label, Button, Frame, PhotoImage, Toplevel, ttk
from PIL import Image, ImageTk
import os
import glob
import subprocess
import smbus
import numpy as np

# Setup GPIO and SMBus
def setup_hardware():
    pins = [21, 23, 27] # To activate the digipot
    for pin in pins:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)

    bus = smbus.SMBus(1)
    device_address = 0x2E # Address of the digipot@
    register_address = 0x00
    intensity = 0xFF  # IR Intensity
    bus.write_byte_data(device_address, register_address, intensity)

    GPIO.setup(12, GPIO.OUT)  # LED PIN
    GPIO.setup(5, GPIO.OUT)  # IR PIN
    GPIO.output(5, GPIO.HIGH)

setup_hardware()

# Global variables
picam2 = None
root = None
frame_container = None
capture_thread = None
gallery_process = None
device_address = 0x2E
register_address = 0x00
bus = smbus.SMBus(1)

# Showing the Live feed
def update_image(label, frame_container):
    if frame_container['frame'] is not None:
        gray_image = cv2.cvtColor(frame_container['frame'], cv2.COLOR_BGR2GRAY)
        pil_image = Image.fromarray(gray_image)
        imgtk = ImageTk.PhotoImage(image=pil_image)
        label.imgtk = imgtk
        label.config(image=imgtk)
    if frame_container['running']:
        label.after(67, update_image, label, frame_container)

#Capturing images to show in the live feed
def capture_frames(picam2, frame_container):
    while frame_container['running']:
        frame_container['frame'] = picam2.capture_array()
        time.sleep(1 / 15)  # 15 FPS

# Function to tigger white led for 700ms
def trigger_flash():
    GPIO.output(5, GPIO.LOW)
    intensity = 0xFF ## White light intensity(Temporarily set as max value)
    bus.write_byte_data(device_address, register_address, intensity)
    # time.sleep(0.4)
    GPIO.output(12, GPIO.HIGH)
    time.sleep(0.7)
    GPIO.output(12, GPIO.LOW)
    intensity = 0xFF ## IR Intensity
    bus.write_byte_data(device_address, register_address, intensity)
    GPIO.output(5, GPIO.HIGH)

#Function to capture images
def capture_high_res_image(picam2, preview_config, thumbnail_label, frame_container):
    # Creating folders and generating file names
    if not os.path.exists('test_captured'):
        os.makedirs('test_captured')
    filename = f"test_captured/capture_{int(time.time())}.jpg"
    ir_filename = f"test_captured/capture_{int(time.time())}_IR.jpg"

    # Picamera configuration
    controls = {"ExposureTime": 66657, "ColourGains": (1.5, 3.0),"AnalogueGain": 7.5}
    high_res_config = picam2.create_still_configuration(main={"size": (2028, 960)}, controls=controls)
    picam2.switch_mode(high_res_config)
    picam2.start()

    #Capturing IR Image
    request = picam2.capture_request()
    if request:
        cv_image = request.make_array('main')
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        Image.fromarray(gray_image).save(ir_filename)
        request.release()

    # Capaturing Red reflex
    # The LED is triggerd in a seperate thread to ensure the flash is synced with the image capture
    flash_thread = threading.Thread(target=trigger_flash)
    flash_thread.start()

    request = picam2.capture_request()
    if request:
        cv_image = request.make_array('main')
        Image.fromarray(cv_image).save(filename)
        request.release()

    metadata = picam2.capture_metadata()
    print("capture metadata:\n")
    controls = {c: metadata[c] for c in ["ExposureTime", "AnalogueGain", "ColourGains"]}
    print(controls)
    print("\n")
    print("all:\n")
    print(metadata)

    flash_thread.join()

    # Updating the preview thumbnail
    update_thumbnail(thumbnail_label)
    picam2.switch_mode(preview_config)
    picam2.start()

def update_thumbnail(thumbnail_label):
    try:
        latest_file = max(glob.glob('test_captured/*'), key=os.path.getctime)
        img = Image.open(latest_file)
        img.thumbnail((48, 32), Image.Resampling.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img)
        thumbnail_label.config(image=imgtk)
        thumbnail_label.image = imgtk
    except ValueError:
        pass

def create_status_popup(message):
    popup = Toplevel(root)
    popup.title("Status")
    popup.geometry('480x320')
    popup.attributes('-fullscreen', True)
    ttk.Label(popup, text=message, font=('Helvetica', 12)).pack(expand=True, padx=20, pady=20)
    return popup

def open_gallery():
    popup = create_status_popup("Opening gallery...")
    gallery_process = subprocess.Popen(['python', 'test_gallery.py'])
    root.after(150, popup.destroy)

def main():
    global picam2, root, frame_container, capture_thread
    picam2 = Picamera2()

    # Picamera configuration for live feed
    controls = {"ExposureTime": 66657, "ColourGains": (1.5, 3.0)}
    preview_config = picam2.create_preview_configuration(main={"size": (676, 320)}, controls=controls)
    picam2.configure(preview_config)
    picam2.start()
    time.sleep(3)

    frame_container = {'frame': None, 'running': True}
    capture_thread = threading.Thread(target=capture_frames, args=(picam2, frame_container))
    capture_thread.start()

    root = Tk()
    root.attributes('-fullscreen', True)

    frame = Frame(root)
    frame.pack(side='bottom', fill='x')

    lbl = Label(root)
    lbl.pack(fill='both', expand=True)

    camera_img = PhotoImage(file="assets/camera_icon.png")
    quit_img = PhotoImage(file="assets/red_x_icon.png")

    quit_button = Button(frame, image=quit_img, command=lambda: cleanup(root, picam2, frame_container, capture_thread))
    quit_button.image = quit_img
    quit_button.pack(side='left')

    thumbnail_label = Label(frame)
    thumbnail_label.pack(side='right')
    thumbnail_label.bind("<Button-1>", lambda e: open_gallery())

    capture_button = Button(frame, image=camera_img, command=lambda: capture_high_res_image(picam2, preview_config, thumbnail_label,frame_container))
    capture_button.image = camera_img
    capture_button.pack(side='top')

    update_thumbnail(thumbnail_label)
    update_image(lbl, frame_container)
    root.mainloop()

def cleanup(root, picam2, frame_container, capture_thread):
    frame_container['running'] = False
    capture_thread.join()
    picam2.stop()
    GPIO.cleanup()
    root.destroy()

if __name__ == "__main__":
    main()
