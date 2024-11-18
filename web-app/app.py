import os
import base64
import requests
from flask import Flask, render_template, make_response, request, redirect, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId

def create_app():

    app = Flask(__name__)

    client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017/"))
    db = client.test

    if client is None:
        raise ValueError("Error with URI")

    try:
        client = MongoClient(client)
        db = client.get_database("ASL-DB")
        images_collection = db["images"]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Error: {e}")

    @app.route("/")
    def home():
        # returns rendered html
        return render_template("index.html")
    

    @app.route("/upload_snapshot", methods=["POST"])
    def upload_video():
        try: 
            data = request.json
            image_data = data.get("image")

            if not image_data:
                return jsonify({"error": "No image data received"}), 400
            image_data = image_data.split(",")[1]
            image_binary = base64.b64decode(image_data)

            image_doc = {"image": image_binary, "translation": None}
            result = images_collection.insert_one(image_doc)

            image_id = str(result.inserted_id)

            return jsonify({"message": "Snapshot saved successfully!"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

    
        # TO DO


    @app.route("/history")
    def view_history():
        try: 
            images = images_collection.find({}, {"_id": 1, "translation":1})
            history = [{"image_id": str(image["_id"]), "translation": images}]
            return render_template("display.html")
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # @app.route("/display_images")
    # def display_images():
    #     images = db.images.find()
    #     return render_template("display_images.html", images=images)

    @app.route("/upload_image", methods=["POST"])
    def upload_image():
        image_data = request.form["image_data"]
        if image_data != "test":
            image_id = db.images.insert_one({"image_data": image_data}).inserted_id
            # is this URL correct?
            ml_client_url = "http://machine_learning_client:5001/processImage"
            response = requests.post(ml_client_url, json={"image_id": str(image_id)})
            if response.status_code == 200:
                return redirect(url_for("display_images"))
            else:
                return "Error processing image"


    def get_data():

        # TO DO
        
        return
    

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app = create_app()
    app.run(port=FLASK_PORT)