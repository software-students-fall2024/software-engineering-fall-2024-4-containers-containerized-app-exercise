import pymongo
import os
import certifi
from dotenv import load_dotenv
import logging
from flask import request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

mongo_cxn = os.getenv('MONGO_CXN_STRING')
logger.info(mongo_cxn)

client = pymongo.MongoClient(mongo_cxn, tlsCAFile=certifi.where())

db = client['project4']
collection = db['num_classifications']


def save_to_mongo(data):
    try:
        document = {
            'intended_num': data['intendedNum'],
            'classified_num': data['classifiedNum'],
            'image_data': data['imageData'],
        }

        result = collection.insert_one(document)
        logger.info(f"Document saved to MongoDB with ig: {result.inserted_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving to MongoDB: {str(e)}")
        return False
