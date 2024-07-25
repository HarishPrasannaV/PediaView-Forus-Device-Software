import qrcode
from PIL import Image
import json
from datetime import datetime

def generate_qr(name, age, mrn):
    # Current timestamp
    current_time = datetime.now().isoformat()

    # Create a dictionary with the data
    data = {
        "Name": name,
        "Age": age,
        "MRN": mrn,
        "Timestamp": current_time
    }

    # Convert dictionary to JSON string
    json_data = json.dumps(data)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill='black', back_color='white')

    # Save it somewhere, change the path as needed
    img.save("patient_qr.png")

    return img

if __name__ == "__main__":
    # Input data
    name = input("Enter name: ")
    age = input("Enter age: ")
    mrn = input("Enter MRN: ")

    # Generate QR code
    image = generate_qr(name, age, mrn)
    image.show()  # This will display the image with your default image viewer
