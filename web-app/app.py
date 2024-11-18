import os
from flask import Flask, render_template, make_response, request, redirect, url_for
from pymongo import MongoClient
import os

def create_app():

    app = Flask(__name__)

    MONGO_URI = os.getenv("MONGO_URI")

    if MONGO_URI is None:
        raise ValueError("Error with URI")
    
    try:
        client = MongoClient(MONGO_URI)
        db = client.get_database("ASL-DB")
        images_collection = db["entries"]
        print("Connected")
    except Exception as e:
        print(f"Error: {e}")

    @app.route("/")
    def home():
        # returns rendered html
        return render_template("index.html")
    
    @app.route("/upload_video", methods=["POST"])
    def upload_video():
        try: 
            data = request.json
            image_data = data.get("image")

            if not image_data:
                return jsonify({"error": "No image data received"}), 400
            image_data = image_data.split(",")[1]
            image_binary = base64.b64decode(image_data)

            image_id = str(result.inserted_id)

            result = images_collection.insert_one({"image": image_binary})
            return jsonify({"message": "Snapshot saved successfully!"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

    
        # TO DO

    @app.route("/display")
    def display():
        images = images_collection.find({}, {"_id": 1, "translation":1})
        history = [{"image_id": str(image["_id"]), "translation": images}]
    def get_data():

        # TO DO
        
        return
    

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app = create_app()
    app.run(port=FLASK_PORT)