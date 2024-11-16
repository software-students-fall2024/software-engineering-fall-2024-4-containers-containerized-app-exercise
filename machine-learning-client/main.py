"""
ML Client Script

This script connects to a MongoDB database and keeps the connection alive.
"""

import os
import time
import pymongo

def main():
    """
    Main function to connect to MongoDB and keep the client running.

    It connects to the MongoDB database specified by the MONGO_URI
    environment variable
    """
    mongo_uri = os.getenv("MONGO_URI")
    client = pymongo.MongoClient(mongo_uri)
    db = client['sensor_data']
    
    print(f"Connected to MongoDB database: {db.name}")
    
    try:
        while True:
            print("ML client is connected and running...")
            time.sleep(10)
    except KeyboardInterrupt:
        print("ML client is shutting down...")
    finally:
        client.close()

if __name__ == "__main__":
    main()
