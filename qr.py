import cv2
from picamera2 import Picamera2
from tkinter import Tk, Label, Button, Frame, PhotoImage, Toplevel, Entry, StringVar
from PIL import Image, ImageTk
import json
from pyzbar.pyzbar import decode

# Global variables
global picam2, root

# Updating each frame in GUI
def update_image(label):
    frame = picam2.capture_array()
    cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv_image)
    imgtk = ImageTk.PhotoImage(image=pil_image)
    label.imgtk = imgtk
    label.config(image=imgtk)

    # Detecting and Decoding QR from the frame
    decoded_objects = decode(pil_image)
    if decoded_objects:
        data = decoded_objects[0].data.decode('utf-8')
        try:
            json_data = json.loads(data)
            create_confirmation_popup(json_data)
        except json.JSONDecodeError:
            create_confirmation_popup({"Error": "QR Code does not contain valid JSON."})

    # Update the image in the label periodically
    label.after(100, update_image, label)

def create_confirmation_popup(json_data):
    popup = Toplevel(root)
    popup.title("Confirmation")
    popup.attributes('-fullscreen', True)

    # Create a frame for JSON data fields
    data_frame = Frame(popup)
    data_frame.pack(fill='both', expand=True, pady=10)

    # Dynamically create labels and entries for each JSON key-value pair
    for key, value in json_data.items():
        Label(data_frame, text=f"{key}:", font=("Helvetica", 12)).pack(anchor='w')
        var = StringVar()
        var.set(value)
        entry = Entry(data_frame, textvariable=var, font=("Helvetica", 12), state='readonly')
        entry.pack(fill='x', padx=20)

    # Load icons for buttons
    yes_img = PhotoImage(file="assets/green_t_icon.png")
    no_img = PhotoImage(file="assets/red_x_icon.png")

    # Control buttons with icons
    Button(popup, image=yes_img, command=lambda: placeholder_action(popup)).pack(side='left', padx=10, pady=10)
    Button(popup, image=no_img, command=popup.destroy).pack(side='right', padx=10, pady=10)

    # Store a reference to the images to avoid garbage collection
    popup.yes_img = yes_img
    popup.no_img = no_img

def placeholder_action(popup):
    # Placeholder for future action
    print("Yes was clicked")
    popup.destroy()
    root.destroy()

def setup_gui():
    global root
    root = Tk()
    root.title("QR Code Scanner")
    root.attributes('-fullscreen', True)

    main_frame = Frame(root)
    main_frame.pack(fill='both', expand=True)

    quit_img = PhotoImage(file="assets/red_x_icon.png")
    quit_button = Button(main_frame, image=quit_img, command=root.destroy)
    quit_button.image = quit_img  # Keep a reference to avoid garbage collection
    quit_button.pack(side='bottom', pady=10)

    lbl = Label(main_frame)
    lbl.pack(fill='both', expand=True)
    update_image(lbl)

def main():
    global picam2
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(preview_config)
    picam2.start()

    setup_gui()
    root.mainloop()

if __name__ == "__main__":
    main()
