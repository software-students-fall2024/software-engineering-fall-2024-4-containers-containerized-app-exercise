import face_recognition
from flask import Flask, request, jsonify
import cv2

app = Flask(__name__)


@app.route("/encode", methods=["POST"])
def encode_image():
    data = request.get_json()
    image_path = data.get("image_path")

    if not image_path:
        return jsonify({"error": "Image path is required"}), 400

    try:
        # Load the image using face_recognition
        image = face_recognition.load_image_file(image_path)
        # Convert the image to RGB format if necessary (OpenCV usually loads images in BGR format)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            return jsonify({"error": "No face found in the image"}), 400

        # Return the first encoding (we assume there's only one face for registration)
        return jsonify({"encoding": encodings[0].tolist()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/verify", methods=["POST"])
def verify_identity():
    data = request.get_json()
    image_path = data.get("image_path")
    stored_encoding = data.get("stored_encoding")

    if not image_path or not stored_encoding:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Convert the stored encoding from list to a numpy array
        stored_encoding = [float(num) for num in stored_encoding]

        # Load the uploaded image and generate its encoding
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            return jsonify({"error": "No face found in the image"}), 400

        # Compare the new encoding with the stored encoding
        match = face_recognition.compare_faces([stored_encoding], encodings[0])[0]

        if match:
            return jsonify({"result": "verified"}), 200
        else:
            return jsonify({"result": "not verified"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001)
