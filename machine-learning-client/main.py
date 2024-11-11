"""
Main module for sound classification using audio recording and feature extraction.

This script records audio, extracts audio features, and classifies the sound
using a pre-trained K-Nearest Neighbors (KNN) model. It includes functions for
recording, feature extraction, model training, loading, and classification.
"""

import os
import pickle
from datetime import datetime

import librosa
import numpy as np
import sounddevice as sd
from sklearn.neighbors import KNeighborsClassifier


def record_audio(duration=2, fs=44100):
    """Record audio from the microphone."""
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    print("Recording complete.")
    return np.squeeze(audio)


def extract_features(audio, fs):
    """Extract audio features using MFCC."""
    mfccs = librosa.feature.mfcc(y=audio, sr=fs, n_mfcc=40)
    mfccs_mean = np.mean(mfccs.T, axis=0)
    return mfccs_mean


def train_model():
    """Train a simple KNN model with pre-recorded samples."""
    # Labels: 0 - Clapping, 1 - Snapping, 2 - Hitting Desk
    x_data = []
    y_labels = []

    data_dir = "training_data"
    labels = {"clapping": 0, "snapping": 1, "hitting": 2}

    for label, idx in labels.items():
        label_dir = os.path.join(data_dir, label)
        for file_name in os.listdir(label_dir):
            if file_name.endswith(".wav"):
                file_path = os.path.join(label_dir, file_name)
                audio, fs = librosa.load(file_path, sr=None)
                features = extract_features(audio, fs)
                x_data.append(features)
                y_labels.append(idx)

    x_data = np.array(x_data)
    y_labels = np.array(y_labels)

    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(x_data, y_labels)

    # Save the trained model
    with open("sound_classification_model.pkl", "wb") as file:
        pickle.dump(model, file)

    print("Model trained and saved.")


def load_model():
    """Load the trained model."""
    if not os.path.exists("sound_classification_model.pkl"):
        train_model()
    with open("sound_classification_model.pkl", "rb") as file:
        model = pickle.load(file)
    return model


def classify_sound(model, features):
    """Classify the sound using the loaded model."""
    prediction = model.predict([features])[0]
    labels = {0: "clapping", 1: "snapping", 2: "hitting the desk"}
    return labels[prediction]


def main():
    """Main function to run the client."""
    try:
        fs = 44100
        duration = 4  # Duration in seconds
        audio = record_audio(duration=duration, fs=fs)

        # Extract features
        features = extract_features(audio, fs)

        # Load model
        model = load_model()

        # Classify sound
        result = classify_sound(model, features)

        # Prepare metadata
        metadata = {
            "timestamp": datetime.utcnow(),
            "classification": result,
        }
        print(metadata)

        print(f"Sound classified as: {result}")
        print("Metadata saved successfully.")

    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except OSError as e:
        print(f"OS error: {e}")

if __name__ == "__main__":
    main()
