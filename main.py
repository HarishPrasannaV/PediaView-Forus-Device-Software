import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time

def start_screening():
    run_script_with_popup('scanNcapture.py', "Wait...")

def test_screening():
    run_script_with_popup('capture.py', "Wait...")

def qr_test():
    run_script_with_popup('qr.py', "Wait...")

def open_gallery():
    run_script_with_popup('gallery.py', "Wait...")

def test_gallery():
    run_script_with_popup('test_gallery.py', "Wait...")

def run_script_with_popup(script_name, message):
    # Display a pop-up window with a status message
    popup = create_status_popup(message)
    popup.update()

    def run_script():
        try:
            subprocess.run(['python', script_name], check=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running {script_name}: {e}")
        finally:
            # Close the pop-up window after the script starts running
            time.sleep(6)
            popup.destroy()

    threading.Thread(target=run_script).start()

def create_status_popup(message):
    # Create a top-level window for the status message
    popup = tk.Toplevel(root)
    popup.title("Status")
    popup.geometry('480x320')  # Set the window size
    popup.attributes('-fullscreen', True)  # Open the pop-up window in fullscreen mode
    ttk.Label(popup, text=message, font=('Helvetica', 12)).pack(expand=True, padx=20, pady=20)
    return popup

def quit_application():
    root.destroy()

def show_extras_menu(event):
    extras_menu.post(event.x_root, event.y_root)

root = tk.Tk()
root.title("Main Application")

# Configure the root window for fullscreen and set a fixed size
root.geometry('480x320')  # Set the window size
root.attributes('-fullscreen', True)  # Open the window in fullscreen mode

# Create a frame to hold the buttons and label
frame = ttk.Frame(root)
frame.pack(pady=20)

# Load icons for buttons
start_icon = tk.PhotoImage(file="assets/start_icon.png")
gallery_icon = tk.PhotoImage(file="assets/gallery_icon.png")
quit_icon = tk.PhotoImage(file="assets/quit.png")
test_icon = tk.PhotoImage(file="assets/camera.png")
qr_icon = tk.PhotoImage(file="assets/qr.png")
tg_icon = tk.PhotoImage(file="assets/tg.png")
extras_icon = tk.PhotoImage(file="assets/extras_icon.png")

# Configure grid layout
frame.columnconfigure((0, 1, 2, 3), weight=1)
frame.rowconfigure((0, 1), weight=1)

# Start Screening button
start_button = ttk.Button(frame, image=start_icon, command=start_screening)
start_button.image = start_icon  # Keep a reference
start_button.grid(row=0, column=0, padx=10, pady=10)

# Gallery button
gallery_button = ttk.Button(frame, image=gallery_icon, command=open_gallery)
gallery_button.image = gallery_icon  # Keep a reference
gallery_button.grid(row=0, column=1, padx=10, pady=10)

# Test button
test_button = ttk.Button(frame, image=test_icon, command=test_screening)
test_button.image = test_icon  # Keep a reference
test_button.grid(row=0, column=2, padx=10, pady=10)

# Extras button with dropdown menu
extras_button = ttk.Button(frame, image=extras_icon)
extras_button.image = extras_icon  # Keep a reference
extras_button.grid(row=1, column=0, padx=10, pady=10)
extras_button.bind("<Button-1>", show_extras_menu)

# Quit button
quit_button = ttk.Button(frame, image=quit_icon, command=quit_application)
quit_button.image = quit_icon  # Keep a reference
quit_button.grid(row=1, column=2, padx=10, pady=10)

# Create the extras dropdown menu
extras_menu = tk.Menu(root, tearoff=0)
extras_menu.add_command(label="QR Test", command=qr_test)
extras_menu.add_command(label="Test Gallery", command=test_gallery)

root.mainloop()
