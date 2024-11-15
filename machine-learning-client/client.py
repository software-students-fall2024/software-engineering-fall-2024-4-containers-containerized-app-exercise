#Client
import cv2  # OpenCV for video capture
import pymongo  # MongoDB client
import time
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = pymongo.MongoClient(mongo_uri)
db = client['productivity_db']
collection = db['focus_data']

def capture_focus_data():
    # OpenCV video capture setup
    cap = cv2.VideoCapture(0)  # Use the first camera connected to your computer

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Placeholder: Focus detection logic to be implemented here
        focus_metric = {"timestamp": time.time(), "focus_score": 0.75}  # Dummy value for now
        
        # Save to MongoDB
        collection.insert_one(focus_metric)

         # Display the frame with a simple message
        cv2.putText(frame, "Focus Score: 0.75", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255, 0, 0), 2, cv2.LINE_AA)
        
        # Display the frame
        cv2.imshow('Focus Monitor', frame)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting focus monitor...")
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        capture_focus_data()
    except Exception as e:
        print(f"An error occurred rip: {e}")
