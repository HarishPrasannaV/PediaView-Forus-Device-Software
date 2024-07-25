import os
import glob
import tkinter as tk
from tkinter import ttk, Label, PhotoImage, Toplevel
from PIL import Image, ImageTk

def display_images():
    if os.path.exists('test_captured') and os.path.isdir('test_captured'):
        image_files = sorted(
            glob.glob('test_captured/*.png') +
            glob.glob('test_captured/*.jpg') +
            glob.glob('test_captured/*.jpeg'),
            key=os.path.getmtime, reverse=True
        )
        if image_files:
            show_images(image_files)
        else:
            display_message("No images found in 'test_captured' folder.")
    else:
        display_message("No 'test_captured' folder found.")

def show_images(image_files):
    window = Toplevel(root)
    window.title("Image Gallery")
    window.geometry("480x320")
    window.attributes('-fullscreen', True)

    frame = ttk.Frame(window)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    img_label = Label(frame)
    img_label.pack(expand=True)

    current_index = [0]

    def update_image(new_index):
        img = Image.open(image_files[new_index])
        img.thumbnail((430, 320))
        photo = ImageTk.PhotoImage(img)
        img_label.config(image=photo)
        img_label.image = photo
        current_index[0] = new_index

    btn_frame = ttk.Frame(window)
    btn_frame.pack(fill='x')

    # Load icons for buttons
    left_icon = PhotoImage(file="assets/left_arrow.png")
    right_icon = PhotoImage(file="assets/right_arrow.png")
    quit_icon = PhotoImage(file="assets/red_x_icon.png")

    # Buttons with icons
    prev_button = ttk.Button(btn_frame, image=left_icon, command=lambda: update_image((current_index[0] - 1) % len(image_files)))
    prev_button.image = left_icon
    prev_button.pack(side='left')

    next_button = ttk.Button(btn_frame, image=right_icon, command=lambda: update_image((current_index[0] + 1) % len(image_files)))
    next_button.image = right_icon
    next_button.pack(side='right')

    quit_button = ttk.Button(btn_frame, image=quit_icon, command=quit_application)
    quit_button.image = quit_icon
    quit_button.pack(side='bottom', pady=10)

    update_image(0)

def display_message(message):
    window = Toplevel(root)
    window.title("Message")
    window.geometry("480x320")
    window.attributes('-fullscreen', True)
    Label(window, text=message, font=('Helvetica', 16)).pack(padx=20, pady=20)

    # Quit button for the message window
    quit_icon = PhotoImage(file="assets/red_x_icon.png")
    quit_button = ttk.Button(window, image=quit_icon, command=quit_application)
    quit_button.image = quit_icon
    quit_button.pack(pady=10)

def quit_application():
    root.destroy()  # This will close the main window and all child windows

root = tk.Tk()
root.title("Image Viewer")
root.geometry("480x320")
root.attributes('-fullscreen', True)

root.after(100, display_images)

root.mainloop()
