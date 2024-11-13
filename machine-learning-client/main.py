"""
Main module for sound classification using audio recording and feature extraction.

This script records audio, extracts audio features, and classifies the sound
using a pre-trained K-Nearest Neighbors (KNN) model. It includes functions for
recording, feature extraction, model training, loading, and classification.
"""

import io
import os
import pickle
from datetime import datetime

import librosa
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from pydub import AudioSegment
from sklearn.neighbors import KNeighborsClassifier

app = Flask(__name__)
CORS(app)


app = Flask(__name__)
CORS(app)


def extract_features(audio, fs):
    """Extract audio features using MFCC."""
    # Print the shape and sample rate of the audio data
    print(
        f"Extracting features from audio data of shape {audio.shape} with sampling rate {fs}"
    )

    mfccs = librosa.feature.mfcc(y=audio, sr=fs, n_mfcc=40)
    mfccs_mean = np.mean(mfccs.T, axis=0)

    # Print the shape and values of the extracted features
    print(f"Extracted MFCCs shape: {mfccs.shape}")
    print(f"Extracted MFCCs mean shape: {mfccs_mean.shape}")
    print(f"Extracted MFCCs mean values: {mfccs_mean}")

    return mfccs_mean


def train_model():
    """Train a simple KNN model with pre-recorded samples."""
    print("Starting model training...")
    x_data = []
    y_labels = []

    data_dir = "./training_data"
    labels = {"clapping": 0, "snapping": 1, "hitting": 2}

    for label, idx in labels.items():
        label_dir = os.path.join(data_dir, label)
        print(f"Processing training data for label '{label}' with index {idx}")
        for file_name in os.listdir(label_dir):
            if file_name.endswith(".wav"):
                file_path = os.path.join(label_dir, file_name)
                audio, fs = librosa.load(file_path, sr=None)
                features = extract_features(audio, fs)
                x_data.append(features)
                y_labels.append(idx)

    x_data = np.array(x_data)
    y_labels = np.array(y_labels)

    # Print the shapes of the training data and labels
    print(f"Training data shape: {x_data.shape}")
    print(f"Training labels shape: {y_labels.shape}")
    print(f"Training labels: {y_labels}")

    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(x_data, y_labels)

    # Save the trained model
    with open("sound_classification_model.pkl", "wb") as file:
        pickle.dump(model, file)

    print("Model trained and saved successfully.")


def load_model():
    """Load the trained model."""
    print("Loading model...")
    train_model()
    with open("sound_classification_model.pkl", "rb") as file:
        model = pickle.load(file)
    print("Model loaded successfully.")
    return model


def classify_sound(model, features):
    """Classify the sound using the loaded model."""
    print(f"Classifying sound with features: {features}")
    prediction = model.predict([features])[0]
    labels = {0: "clapping", 1: "snapping", 2: "hitting the desk"}
    print(f"Prediction index: {prediction}, Predicted label: {labels[prediction]}")
    return labels[prediction]


@app.route("/classify", methods=["POST"])
def classify():
    """Handle the classification request from the client."""
    try:
        print("Received classification request...")
        # Check if audio file is in the request
        if "audio" not in request.files:
            print("No audio file provided in the request.")
            return jsonify({"error": "No audio file provided"}), 400
        audio_file = request.files["audio"]
        audio_bytes = audio_file.read()

        # Use pydub to read the audio data
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        print(f"Audio segment duration: {audio_segment.duration_seconds} seconds")
        print(f"Audio segment frame rate: {audio_segment.frame_rate} Hz")
        print(f"Audio segment sample width: {audio_segment.sample_width} bytes")

        # Convert to mono and get raw audio data
        audio_segment = audio_segment.set_channels(1)
        audio_data = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
        fs = audio_segment.frame_rate

        # Normalize audio data
        sample_width = audio_segment.sample_width  # in bytes
        max_val = float(2 ** (8 * sample_width - 1) - 1)
        audio_data = audio_data / max_val

        print(f"Received audio data shape: {audio_data.shape}, Sampling rate: {fs}")

        # Extract features
        features = extract_features(audio_data, fs)

        # Load model
        model = load_model()

        # Classify sound
        result = classify_sound(model, features)

        # Prepare metadata
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "classification": result,
        }

        print(f"Classification result: {metadata}")

        return jsonify(metadata), 200
    except KeyError as e:
        print(f"KeyError during classification: {e}")
        return jsonify({"error": "Missing required data"}), 400
    except ValueError as e:
        print(f"ValueError during classification: {e}")
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error during classification: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
