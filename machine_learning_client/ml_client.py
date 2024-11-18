"""
This is the machine learning client code.
"""

import json
from flask import Flask, request, jsonify
import face_recognition
import numpy as np
from PIL import UnidentifiedImageError

app = Flask(__name__)


def encode_face_image(image_file):
    """
    Encode face from image bytes
    """
    try:
        image = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return None, "No face detected in the image."
        return encodings[0], None
    except UnidentifiedImageError:
        return None, "Invalid image file."
    except RuntimeError as e:
        return None, f"Face recognition error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


def recognize_face_encodings(stored_encodings, image_file):
    """
    Recognize face from image bytes
    """
    try:
        test_image = face_recognition.load_image_file(image_file)
        test_encodings = face_recognition.face_encodings(test_image)
        if not test_encodings:
            return "no_face", None, "No face detected in the test image."

        test_encoding = test_encodings[0]
        stored_encodings = [np.array(enc) for enc in stored_encodings]
        results = face_recognition.compare_faces(stored_encodings, test_encoding)
        if any(results):
            matched_index = results.index(True)
            return "verified", matched_index, None
        else:
            return "not_recognized", None, None
    except UnidentifiedImageError:
        return "error", None, "Invalid image file."
    except RuntimeError as e:
        return "error", None, f"Face recognition error: {e}"
    except Exception as e:
        return "error", None, f"Unexpected error: {e}"


@app.route("/encode_face", methods=["POST"])
def encode_face_route():
    """
    Encode face from image bytes
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    encoding, error = encode_face_image(file)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"encoding": encoding.tolist()}), 200


@app.route("/recognize_face", methods=["POST"])
def recognize_face_route():
    """
    Recognize face from image bytes
    """
    if "file" not in request.files or "stored_encodings" not in request.form:
        return jsonify({"error": "Invalid request data"}), 400

    file = request.files["file"]
    stored_encodings_str = request.form.get("stored_encodings")
    # Deserialize stored_encodings from JSON string to Python object
    stored_encodings = json.loads(stored_encodings_str)
    result, matched_index, error = recognize_face_encodings(stored_encodings, file)
    if error:
        return jsonify({"error": error}), 400
    response_data = {"result": result}
    if matched_index is not None:
        response_data["matched_index"] = matched_index
    return jsonify(response_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
