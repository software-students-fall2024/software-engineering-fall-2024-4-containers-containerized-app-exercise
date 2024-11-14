"""
This module processes audio files, performs transcription and sentiment analysis,
and stores the results in a MongoDB database.
"""
import os
import logging
from datetime import datetime
from pickletools import pylong
from pymongo import MongoClient
from dotenv import load_dotenv
from utils import get_audio_files, transcribe_audio, analyze_sentiment, store_data

def setup_logging():
    """
    Sets up logging configuration for the application.
    
    This function configures logging to output messages to the console with a
    specific format and at the DEBUG level.
    """
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def main():
    """
    Main function to run the audio processing and sentiment analysis pipeline.
    
    This function loads environment variables, connects to the MongoDB database,
    processes each audio file in the specified directory, transcribes it, performs
    sentiment analysis, and stores the data in MongoDB. If no audio files are found,
    it logs a warning message.
    """
    load_dotenv()
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://root:voice_mood@localhost:27017')
    audio_dir = os.getenv('AUDIO_DIR', './audio')
    setup_logging()
    logger = logging.getLogger(__name__)
    try:
        client = MongoClient(mongo_uri)
        db = client['voice_mood_journal']
        collection = db['entries']
        logger.info("Connected to MongoDB.")
    except pymongo.errors.ConnectionFailure as e:
        logger.error("Failed to connect to MongoDB: %s", e)
        return

    audio_files = get_audio_files(audio_dir)
    """
    Retrieves audio files from the specified directory.
    """
    if not audio_files:

        logger.warning("There are no audio files in the directory.")
        return

    for file_path in audio_files:
        try:
            logger.info("Processing file: %s", file_path)
            text = transcribe_audio(file_path)
            logger.debug("Transcription: %s", text)
            sentiment = analyze_sentiment(text)
            logger.debug("Sentiment: %s", sentiment)

            data = {
                'file_name': os.path.basename(file_path),
                'transcript': text,
                'sentiment': sentiment,
                'timestamp': datetime.utcnow()
            }

            store_data(collection, data)
            logger.info("Successfully processed and stored data for %s", file_path)

        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error processing %s: %s", file_path, e)
if __name__ == '__main__':
    main()
