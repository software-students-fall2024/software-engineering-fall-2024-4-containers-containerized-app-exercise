import os
import requests
from flask import Flask, render_template, make_response, request, redirect, url_for
from pymongo import MongoClient

def create_app():

    app = Flask(__name__)

    client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017/"))
    db = client.test

    if client is None:
        raise ValueError("Error with URI")

    try:
        client = MongoClient(client)
        db = client.get_database("ASL-DB")
        collection = db["entries"]
        print("Connected")
    except Exception as e:
        print(f"Error: {e}")

    @app.route("/")
    def home():
        # returns rendered html
        return render_template("index.html")
    
    @app.route("/display_images")
    def display_images():
        images = db.images.find()
        return render_template("display_images.html", images=images)

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