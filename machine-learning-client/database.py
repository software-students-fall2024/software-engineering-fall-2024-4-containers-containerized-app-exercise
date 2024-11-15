from pymongo import MongoClient
from datetime import datetime, timezone

client = MongoClient("mongodb://mongodb_container:27017/")
db = client["productivity_db"]

def save_metrics(focus_level):  # You can also add other parameters like noise_level
    # Using timezone-aware UTC datetime
    db.metrics.insert_one({
        "timestamp": datetime.now(timezone.utc),
        "focus_level": focus_level,
        # "noise_level": noise_level  # Uncomment if you want to save noise level
    })
