import os
from datetime import datetime
import glob
import speech_recognition as sr
from textblob import TextBlob
import logging

def get_audio_files(directory):
    audio_files=glob.glob(os.path.join(directory, '*.wav'))
    return audio_files

def transcribe_audio(file_path):
    recognizer=sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio=recognizer.record(source)
    try:
        text=recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        logging.error("Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        logging.error(f"Could not request results; {e}")
        return ""

def analyze_sentiment(text):
    blob=TextBlob(text)
    polarity=blob.sentiment.polarity
    subjectivity=blob.sentiment.subjectivity

    if polarity>0:
        mood='Positive'
    elif polarity<0:
        mood='Negative'
    else:
        mood='Neutral'

    sentiment={
        'polarity':polarity,
        'subjectivity':subjectivity,
        'mood':mood
    }
    return sentiment

def store_data(collection, data):
    collection.insert_one(data)