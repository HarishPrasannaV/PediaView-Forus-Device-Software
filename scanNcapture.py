import cv2
from picamera2 import Picamera2, Preview
from tkinter import Tk, Label, Button, Frame, PhotoImage, Toplevel, Entry, StringVar, ttk
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import threading
import time
import json
from pyzbar.pyzbar import decode
import os
import glob
import subprocess
import smbus

class ImageCaptureApp:
    def __init__(self):
        self.LED_PIN = 12 # White LED pin
        self.scan_mode = True
        self.images = {}
        self.current_mrn = 'Unknown_MRN'
        self.current_qr_data = {}
        self.frame_container = {'frame': None, 'running': True}
        self.popup = None
        self.thumbnail_label = None

        # Acrivating the Digipot
        pins = [21, 23, 27]
        for pin in pins:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)

        self.bus = smbus.SMBus(1)
        self.device_address = 0x2E ## Address of the digipot
        self.register_address = 0x00
        intensity = 0xFF # Internsity of IR
        self.bus.write_byte_data(self.device_address, self.register_address, intensity)

        #Turning on IR
        GPIO.setmode(GPIO.BCM)
        self.IR_PIN = 5
        GPIO.setup(self.IR_PIN, GPIO.OUT)
        GPIO.output(self.IR_PIN, GPIO.HIGH)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

        # Picamera configuration for live preview
        self.picam2 = Picamera2()
        controls = {"ExposureTime": 66657, "ColourGains": (1.5, 3.0)}
        self.preview_config = self.picam2.create_preview_configuration(main={"size": (676, 320)}, controls=controls)
        self.picam2.configure(self.preview_config)
        self.picam2.start()
        time.sleep(3)

        # Frames are captutred in a speperate thread to optimise perfomance
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.start()

        self.root = Tk()
        self.root.attributes('-fullscreen', True)

        self.load_images()
        self.show_main_gui()
        self.update_thumbnail()  # Initialize thumbnail with the latest image if available

    def load_images(self):
        self.images['camera_img'] = PhotoImage(file="assets/camera_icon.png")
        self.images['quit_img'] = PhotoImage(file="assets/red_x_icon.png")
        self.images['yes_img'] = PhotoImage(file="assets/green_t_icon.png")
        self.images['no_img'] = PhotoImage(file="assets/red_x_icon.png")

    def update_image(self, label):
        # Updating the image in the thumbanail for live camera feed
        if self.frame_container['frame'] is not None:
            cv_image = cv2.cvtColor(self.frame_container['frame'], cv2.COLOR_BGR2GRAY)
            pil_image = Image.fromarray(cv_image)
            imgtk = ImageTk.PhotoImage(image=pil_image)
            label.imgtk = imgtk
            label.config(image=imgtk)
            # Scaing for QR codes
            if self.scan_mode:
                decoded_objects = decode(pil_image)
                if decoded_objects:
                    data = decoded_objects[0].data.decode('utf-8')
                    try:
                        json_data = json.loads(data)
                        self.qr_popup(json_data)
                    except json.JSONDecodeError:
                        self.qr_popup({"Error": "QR Code does not contain valid JSON."})

        if self.frame_container['running']:
            label.after(67, self.update_image, label)  # 15 FPS corresponds to ~67ms per frame

    def qr_popup(self, json_data):
        if self.popup:
            self.popup.destroy()

        self.current_qr_data = json_data
        if 'MRN' in json_data:
            self.current_mrn = json_data['MRN']
        else:
            self.current_mrn = 'Unknown_MRN'

        self.popup = Toplevel(self.root)
        self.popup.title("Confirmation")
        self.popup.attributes('-fullscreen', True)

        data_frame = Frame(self.popup)
        data_frame.pack(fill='both', expand=True, pady=10)

        for key, value in json_data.items():
            Label(data_frame, text=f"{key}:", font=("Helvetica", 12)).pack(anchor='w')
            var = StringVar()
            var.set(value)
            entry = Entry(data_frame, textvariable=var, font=("Helvetica", 12), state='readonly')
            entry.pack(fill='x', padx=20)

        yes_button = Button(self.popup, image=self.images['yes_img'], command=lambda: self.switch_gui('capture'))
        yes_button.pack(side='left', padx=10, pady=10)
        no_button = Button(self.popup, image=self.images['no_img'], command=self.popup.destroy)
        no_button.pack(side='right', padx=10, pady=10)

        yes_button.image = self.images['yes_img']
        no_button.image = self.images['no_img']
# Capturing frames in a container to display it in the live feed
    def capture_frames(self):
        while self.frame_container['running']:
            try:
                self.frame_container['frame'] = self.picam2.capture_array()
                self.frame_container['frame'] = cv2.cvtColor(self.frame_container['frame'], cv2.COLOR_BGR2GRAY)
            except Exception as e:
                print(f"Error capturing frame: {e}")
            time.sleep(1/15)  # 15 FPS

    # Function to trigger LED flash
    def trigger_flash(self):
        try:
            GPIO.output(5, GPIO.LOW)
            intensity = 0xFF ## White light intensity (Temporarily set as max value)
            self.bus.write_byte_data(self.device_address, self.register_address, intensity)
            # time.sleep(0.4)
            GPIO.output(12, GPIO.HIGH)
            time.sleep(0.7)
            GPIO.output(12, GPIO.LOW)
            intensity = 0xFF ## IR Intensity
            self.bus.write_byte_data(self.device_address, self.register_address, intensity)
            GPIO.output(5, GPIO.HIGH)
        except Exception as e:
            print(f"Error triggering flash: {e}")

    def capture_high_res_image(self):
        mrn_directory = f'captured/{self.current_mrn}'
        if not os.path.exists(mrn_directory):
            os.makedirs(mrn_directory)

        timestamp = int(time.time())
        image_filename = f"{mrn_directory}/capture_{timestamp}.jpg"
        ir_filename = f"{mrn_directory}/capture_{timestamp}_IR.jpg"
        data_filename = f"{mrn_directory}/data_{timestamp}.txt"

        # Save QR data to a text file
        with open(data_filename, 'w') as f:
            json.dump(self.current_qr_data, f, indent=4)

        controls = {"ExposureTime": 66657, "ColourGains": (1.5, 3.0),"AnalogueGain": 7.5}
        high_res_config = self.picam2.create_still_configuration(main={"size": (2028, 960)}, controls=controls)
        self.picam2.switch_mode(high_res_config)
        self.picam2.start()

        # IR Image capture
        request = self.picam2.capture_request()
        if request:
            cv_image = request.make_array('main')
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            Image.fromarray(gray_image).save(ir_filename)
            request.release()

        # White Capture
        flash_thread = threading.Thread(target=self.trigger_flash)
        flash_thread.start()

        request = self.picam2.capture_request()
        if request:
            cv_image = request.make_array('main')
            Image.fromarray(cv_image).save(image_filename)
            request.release()

        metadata = self.picam2.capture_metadata()
        print("capture metadata:\n")
        controls = {c: metadata[c] for c in ["ExposureTime", "AnalogueGain", "ColourGains"]}
        print(controls)
        print("\n")
        print("all:\n")
        print(metadata)

        flash_thread.join()



        self.update_thumbnail()
        self.picam2.switch_mode(self.preview_config)
        self.picam2.start()

        # Switch back to main mode
        self.switch_gui('main')

    def update_thumbnail(self):
        try:
            list_of_dirs = glob.glob('captured/*')
            if not list_of_dirs:
                return
            latest_dir = max(list_of_dirs, key=os.path.getctime)
            list_of_files = glob.glob(f'{latest_dir}/*.jpg')
            if not list_of_files:
                return
            latest_file = max(list_of_files, key=os.path.getctime)
            img = Image.open(latest_file)
            img.thumbnail((48, 32), Image.Resampling.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.thumbnail_label.config(image=imgtk)
            self.thumbnail_label.image = imgtk
        except ValueError:
            pass

    def create_status_popup(self, message):
        popup = Toplevel(self.root)
        popup.title("Status")
        popup.geometry('480x320')
        popup.attributes('-fullscreen', True)
        ttk.Label(popup, text=message, font=('Helvetica', 12)).pack(expand=True, padx=20, pady=20)
        return popup

    def open_gallery(self):
        popup = self.create_status_popup("Opening gallery...")
        self.root.after(150, lambda: self.open_gallery_helper(popup))

    def switch_gui(self, to):
        self.scan_mode = (to == 'main')

        for widget in self.root.winfo_children():
            widget.destroy()

        if to == 'main':
            self.show_main_gui()
        elif to == 'capture':
            self.show_capture_gui()

    def show_main_gui(self):
        frame = Frame(self.root)
        frame.pack(side='bottom', fill='x')

        lbl = Label(self.root)
        lbl.pack(fill='both', expand=True)

        quit_button = Button(frame, image=self.images['quit_img'], command=self.cleanup)
        quit_button.pack(side='left')
        quit_button.image = self.images['quit_img']

        self.thumbnail_label = Label(frame)
        self.thumbnail_label.pack(side='right')
        self.thumbnail_label.bind("<Button-1>", lambda e: self.open_gallery())

        self.update_thumbnail()  # Call update_thumbnail here

        self.update_image(lbl)

    def show_capture_gui(self):
        frame = Frame(self.root)
        frame.pack(side='bottom', fill='x')

        lbl = Label(self.root)
        lbl.pack(fill='both', expand=True)

        quit_button = Button(frame, image=self.images['quit_img'], command=lambda: self.switch_gui('main'))
        quit_button.pack(side='left')
        quit_button.image = self.images['quit_img']

        self.thumbnail_label = Label(frame)
        self.thumbnail_label.pack(side='right')
        self.thumbnail_label.bind("<Button-1>", lambda e: self.open_gallery())

        capture_button = Button(frame, image=self.images['camera_img'], command=self.capture_high_res_image)
        capture_button.pack(side='top')
        capture_button.image = self.images['camera_img']

        self.update_thumbnail()  # Call update_thumbnail here

        self.update_image(lbl)

    def open_gallery_helper(self, popup):
        subprocess.Popen(['python', 'gallery.py'])
        self.root.after(150, popup.destroy)

    def cleanup(self):
        self.frame_container['running'] = False
        self.capture_thread.join()
        self.picam2.stop()
        GPIO.cleanup()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageCaptureApp()
    app.run()
