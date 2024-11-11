""" Module for retrieving application statistics from mongodb """

import logging
import os
import pymongo
import certifi
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
mongo_cxn = os.getenv('MONGO_CXN_STRING')
# client = pymongo.MongoClient(mongo_cxn, tlsCAFile=certifi.where())
client = pymongo.MongoClient(mongo_cxn)


db = client['project4']
collection = db['num_classifications']


def get_statistics():
    """ Function to retrieve application statistics from mongodb """
    try:
        # get total count of documents
        total_count = collection.count_documents({})

        # get total number of correct predictions
        correct_predictions = collection.count_documents(
            {"$expr": {"$eq": ["$intended_num", "$classified_num"]}}
        )

        # calculate total accuracy
        overall_accuracy = (correct_predictions / total_count) * 100

        # calculate accuracy for each digit
        individual_digit_stats = {}
        for digit in range(10):

            # count total instances of this digit being drawn
            total_digit = collection.count_documents({"intended_num": digit})
            if total_digit > 0:

                # count correct classifications for this digit
                correct_digit = collection.count_documents({
                    "intended_num": digit,
                    "classified_num": digit
                })

                # calculate accuracy for this digit
                digit_accuracy = (correct_digit / total_digit) * 100

                # save to output dict
                individual_digit_stats[digit] = {
                    "total_attempts": total_digit,
                    "correct_classifications": correct_digit,
                    "accuracy": round(digit_accuracy, 2)
                }
            else:
                individual_digit_stats[digit] = {
                    "total_attempts": 0,
                    "correct_classifications": 0,
                    "accuracy": 0
                }

        return {
            "total_samples": total_count,
            "correct_predictions": correct_predictions,
            "overall_accuracy": round(overall_accuracy, 2),
            "individual_digits": individual_digit_stats
        }

    except ZeroDivisionError as e:
        logger.error("Division by zero error: %s", str(e))
        return {"error": "No data available for statistics calculation"}
    except ValueError as e:
        logger.error("Value error in calculations: %s", str(e))
        return {"error": f"Error in calculations: {str(e)}"}
