from pymongo import MongoClient
import speech_recognition as sr
import numpy as np
import wave
import soundfile as sf
import noisereduce as nr
from datetime import datetime

# MongoDB setup
client = MongoClient("mongodb://database/scoobygang")
db = client.audio_analysis
collection = db.audio_logs

recognizer = sr.Recognizer()

# Analyze the audio for noise
def analyze_noise(audio_file_path, noise_threshold):
    with wave.open(audio_file_path, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        frames = wave_file.readframes(-1)
        amplitude = np.frombuffer(frames, dtype=np.int16)
        duration = len(amplitude) / frame_rate

        # Calculate average amplitude as a proxy for noise level
        avg_amp = np.mean(np.abs(amplitude))
        print(f"Average Amplitude: {avg_amp}")
        print(f"Audio Duration: {duration} seconds")

        # Determine if the audio is noisy
        noise_level = "High" if avg_amp > noise_threshold else "Low"
        print(f"Noise Level: {noise_level}")
        return avg_amp, noise_level

# Noise suppress
def suppress_noise(input_audio_path, output_audio_path):
    data, samplerate = sf.read(input_audio_path)
    y_reduced_noise = nr.reduce_noise(y=data, sr=samplerate)
    sf.write(output_audio_path, y_reduced_noise, samplerate, subtype="PCM_24")
    print(f"Noise reduced audio saved as {output_audio_path}")

# Save data to MongoDB
def save_to_db(audio_file_path, reduced_file_path, avg_amp, noise_level, transcription=None):
    document = {
        "timestamp": datetime.now(),
        "original_file": audio_file_path,
        "processed_file": reduced_file_path,
        "average_amplitude": avg_amp,
        "noise_level": noise_level,
        "transcription": transcription,
    }
    collection.insert_one(document)
    print("Data saved to MongoDB.")

# Speech-to-text conversion
def speech_to_text(noise_threshold):
    input_audio_path = "live_audio.wav"
    reduced_audio_path = "live_audio_reduced.wav"

    print("Listening...")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    with open(input_audio_path, "wb") as f:
        f.write(audio.get_wav_data())

    suppress_noise(input_audio_path, reduced_audio_path)

    avg_amp, noise_level = analyze_noise(reduced_audio_path, noise_threshold)

    if avg_amp < noise_threshold:
        with sr.AudioFile(reduced_audio_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Transcribed Text: {text}")
            save_to_db(input_audio_path, reduced_audio_path, avg_amp, noise_level, text)
        except sr.UnknownValueError:
            print("Could not understand the audio. Possibly noisy.")
            save_to_db(input_audio_path, reduced_audio_path, avg_amp, noise_level)
        except sr.RequestError as e:
            print(f"API error: {e}")
    else:
        print("Skipping transcription due to high noise levels.")
        save_to_db(input_audio_path, reduced_audio_path, avg_amp, noise_level)

# Audio-to-text conversion
def audio_to_text(noise_threshold):
    input_audio_path = "example_audio.wav"
    reduced_audio_path = "example_audio_reduced.wav"

    suppress_noise(input_audio_path, reduced_audio_path)

    avg_amp, noise_level = analyze_noise(reduced_audio_path, noise_threshold)

    if avg_amp < noise_threshold:
        with sr.AudioFile(reduced_audio_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Transcribed Text: {text}")
            save_to_db(input_audio_path, reduced_audio_path, avg_amp, noise_level, text)
        except sr.UnknownValueError:
            print("Could not understand the audio. Possibly noisy.")
            save_to_db(input_audio_path, reduced_audio_path, avg_amp, noise_level)
        except sr.RequestError as e:
            print(f"API error: {e}")
    else:
        print("Skipping transcription due to high noise levels.")
        save_to_db(input_audio_path, reduced_audio_path, avg_amp, noise_level)
