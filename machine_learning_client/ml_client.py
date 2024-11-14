import face_recognition
import cv2
import pymongo
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()


mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = pymongo.MongoClient(mongo_uri)
db = client["attendify"]
users_collection = db["users"]


def encode_face(image_path):
    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            return None, "No face detected in the image."

        return encodings[0], None
    except Exception as e:
        print(f"Error in encode_face: {e}")
        return None, "Error during face encoding."


def recognize_face(stored_encodings, test_image_path):
    try:
        test_image = face_recognition.load_image_file(test_image_path)
        test_encoding = face_recognition.face_encodings(test_image)

        if len(test_encoding) == 0:
            return "no_face", "No face detected in the test image."

        results = face_recognition.compare_faces(stored_encodings, test_encoding[0])
        if any(results):
            return "verified", None
        else:
            return "not_recognized", None
    except Exception as e:
        print(f"Error in recognize_face: {e}")
        return "error", "Error during face recognition."


def save_metadata(encoding, metadata):
    users_collection.insert_one({"encoding": encoding, "metadata": metadata})


def collect_and_save_metadata(image_path):
    encoding, error = encode_face(image_path)
    if error:
        print(f"Error encoding face: {error}")
        return

    metadata = {
        "source": "camera",
        "timestamp": "2024-11-13T15:00:00",
        "notes": "Initial registration",
    }
    save_metadata(encoding.tolist(), metadata)
