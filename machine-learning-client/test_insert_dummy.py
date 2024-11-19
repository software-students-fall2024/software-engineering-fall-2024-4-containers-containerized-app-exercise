from pymongo import MongoClient

# MongoDB connection URI
MONGODB_URI = "mongodb+srv://itsOver:itsOver@itsover.bx305.mongodb.net/?retryWrites=true&w=majority&appName=itsOver"

# Connect to MongoDB
client = MongoClient(MONGODB_URI)

# Select the database and collection
db = client["itsOver"]
camera_collection = db["camera_activity"]

# Insert dummy data
dummy_data = {
    "timestamp": 1693500000.123,
    "is_focused": True,
    "message": "This is a test document."
}

result = camera_collection.insert_one(dummy_data)
print(f"Inserted document ID: {result.inserted_id}")