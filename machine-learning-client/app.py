from pymongo import MongoClient
import numpy as np
import time

def collect_and_analyze_data():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client.ml_data
    collection = db.results

    while True:
        data = {"values": list(np.random.rand(5))}
        collection.insert_one(data)
        print("Data inserted:", data)
        time.sleep(10) 

if __name__ == "__main__":
    collect_and_analyze_data()
