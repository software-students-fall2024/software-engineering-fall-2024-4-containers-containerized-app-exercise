import pymongo
import os
import time

def main():
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
