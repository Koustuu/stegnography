import os
import qrcode
import cv2
from pyzbar.pyzbar import decode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)
UPLOAD_FOLDER = "static"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    qr_code = None
    decoded_message = None
    error = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "generate_qr":
            secret_message = request.form.get("message")
            password = request.form.get("password")

            if secret_message and password:
                qr = qrcode.make(secret_message)
                qr_filename = "qr_code.png"
                qr_path = os.path.join(app.config["UPLOAD_FOLDER"], qr_filename)
                qr.save(qr_path)
                qr_code = qr_filename

        elif action == "decode_qr":
            uploaded_file = request.files.get("qr_image")
            password = request.form.get("password")

            if uploaded_file and password:
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], "uploaded_qr.png")
                uploaded_file.save(file_path)

                image = cv2.imread(file_path)
                decoded_objects = decode(image)

                if decoded_objects:
                    decoded_message = decoded_objects[0].data.decode("utf-8")
                else:
                    error = "Could not decode the QR Code."

    return render_template("index.html", qr_code=qr_code, decoded_message=decoded_message, error=error)

@app.route("/download/<filename>")
def download_qr(filename):
    qr_path = os.path.join("static", filename)
    return send_file(qr_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
