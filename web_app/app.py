import os
import base64
import requests
from flask import (
    Flask,
    render_template,
    make_response,
    request,
    redirect,
    url_for,
    jsonify,
)
from pymongo import MongoClient
from bson import ObjectId


def create_app():

    app = Flask(__name__)
    client = MongoClient("mongodb://mongodb:27017/")

    db = client.asl_db

    # if client is None:
    # raise ValueError("Error with URI")

    # try:
    #     client = MongoClient(client)
    #     db = client.get_database("ASL-DB")
    #     images_collection = db["images"]
    #     print("Connected to MongoDB")
    # except Exception as e:
    #     print(f"Error: {e}")

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
            response = requests.post(
                "http://ml_client:5001/processImage",
                json={
                    "image_id": str(
                        db.images.insert_one(
                            {"image": image_data, "output": "", "translation": ""}
                        ).inserted_id
                    )
                },
            )
            if response.status_code == 200:
                data = response.json()
                return jsonify(
                    {
                        "status": "success",
                        "output": data.get("output"),
                        "translation": data.get("translation"),
                    }
                )  # redirect(url_for("display_images"))
            return "Error processing image"

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/history")
    def view_history():
        try:
            images = db.images.find({}, {"translation": 1, "output": 1})
            images_list = []
            for image in images:
                images_list.append(image)
            return render_template("display.html", images=images_list)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # @app.route("/display_images")
    # def display_images():
    #     images = db.images.find()
    #     return render_template("display_images.html", images=images)

    # @app.route("/upload_image", methods=["POST"])
    # def upload_image():
    #     image_data = request.form["image_data"]
    #     if image_data != "test":
    #         image_id = db.images.insert_one({"image_data": image_data}).inserted_id
    #         ml_client_url = "http://ml_client/processImage"
    #         response = requests.post(ml_client_url, json={"image_id": str(image_id)})

    # if response.status_code == 200:
    #     return redirect(url_for("display_images"))
    # else:
    #     return "Error processing image"

    # def get_data():

    #     # TO DO

    #     return

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5002, debug=True)
