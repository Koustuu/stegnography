import qrcode
from cryptography.fernet import Fernet
from pyzbar.pyzbar import decode
from PIL import Image
import os

# Generate and save the encryption key (Run this once)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load the encryption key
def load_key():
    if not os.path.exists("secret.key"):
        generate_key()
    with open("secret.key", "rb") as key_file:
        return key_file.read()

# Encrypt and generate QR code
def create_stega_qr(secret_message, password):
    key = load_key()
    cipher = Fernet(key)
    encrypted_msg = cipher.encrypt(f"{password}:{secret_message}".encode()).decode()

    qr = qrcode.QRCode()
    qr.add_data(f"hidden:{encrypted_msg}")  # Adding a proper identifier
    qr.make()
    img = qr.make_image(fill="black", back_color="white")

    qr_path = os.path.join("static", "stega_qr.png")
    img.save(qr_path)
    return qr_path

# Decode hidden message
def decode_stega_qr(qr_image_path, password):
    key = load_key()
    cipher = Fernet(key)

    qr_image = Image.open(qr_image_path)
    decoded_data = decode(qr_image)

    if not decoded_data:
        return "No QR code found in the image."

    decoded_text = decoded_data[0].data.decode()

    if "hidden:" in decoded_text:
        _, encrypted_msg = decoded_text.split("hidden:", 1)
        decrypted_msg = cipher.decrypt(encrypted_msg.encode()).decode()
        saved_password, secret_message = decrypted_msg.split(":", 1)

        if saved_password == password:
            return secret_message
        else:
            return "Invalid Password!"
    return "No hidden message found."
