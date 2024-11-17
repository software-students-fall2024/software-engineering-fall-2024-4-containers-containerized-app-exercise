"""
This module sets up the Flask application for the Plant Identifier project.
"""

import os
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, make_response, url_for
import pymongo

# from werkzeug.utils import secure_filename

load_dotenv()


def create_app():
    """Initializes and configures the Flask app"""
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit
    app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

    connection = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = connection[os.getenv("MONGO_DBNAME")]

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if request.method == "POST":
            plant_photo = request.form["photo"]
            plant_name = "placeholder"
            plant_data = {
                "photo":plant_photo,
                "name":plant_name
            }
            new_entry = db.plants.insert_one(plant_data)
            new_entry_id = new_entry.inserted_id
            # file = request.files.get("plant_image")
            # if file:
            #     filename = secure_filename(file.filename)
            #     filepath = os.path.join("uploads", filename)
            #     file.save(filepath)

            #     db.identifications.insert_one(
            #         {"filename": filename, "filepath": filepath}
            #     )
            #     return redirect(url_for("results", filename=filename))
            # return make_response("No file uploaded", 400)

            return redirect(url_for("new_entry", new_entry_id=new_entry_id))
        return render_template('upload.html')

    @app.route("/new_entry", methods=["GET", "POST"])
    def new_entry():
        new_entry_id = request.args.get('new_entry_id')
        entry = ObjectId(new_entry_id)
        document = db.plants.find_one({"_id":entry})
        photo = document["photo"]
        name = document["name"]
        return render_template('new-entry.html', photo=photo, name=name)

    @app.route("/results/<filename>")
    def results(filename):
        result = db.identifications.find_one({"filename": filename})
        if result:
            return render_template("results.html", result=result)
        return make_response("Result not found", 404)

    @app.route("/history")
    def history():
        all_results = list(db.plants.find())
        print(all_results)
        # return render_template("home.html")
        return render_template("history.html", all_results=all_results)

    return app


if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "3000")
    application = create_app()
    application.run(port=FLASK_PORT)
