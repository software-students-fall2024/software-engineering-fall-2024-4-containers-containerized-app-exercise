import os
from pymongo import MongoClient
import logging
from utils import get_audio_files, transcribe_audio, analyze_sentiment, store_data
from dotenv import load_dotenv
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def main():
    load_dotenv()
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://root:voice_mood@localhost:27017')
    AUDIO_DIR = os.getenv('AUDIO_DIR', './audio')
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        client = MongoClient(MONGO_URI)
        db = client['voice_mood_journal']
        collection = db['entries']
        logger.info("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return

    audio_files = get_audio_files(AUDIO_DIR)

    if not audio_files:
        logger.warning("There are no audio files in the directory.")
        return

    for file_path in audio_files:
        try:
            logger.info(f"Processing file: {file_path}")
            text = transcribe_audio(file_path)
            logger.debug(f"Transcription: {text}")
            sentiment = analyze_sentiment(text)
            logger.debug(f"Sentiment: {sentiment}")

            data = {
                'file_name': os.path.basename(file_path),
                'transcript': text,
                'sentiment': sentiment,
                'timestamp': datetime.utcnow()
            }

            store_data(collection, data)
            logger.info(f"Successfully processed and stored data for {file_path}.")

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

if __name__ == '__main__':
    main()
