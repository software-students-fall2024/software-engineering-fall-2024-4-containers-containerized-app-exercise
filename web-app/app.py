"""
This module sets up the Flask application for the Plant Identifier project.
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, make_response
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
            photo_data = request.form["photo"]
            print(photo_data)
            db.plants.insert_one({"photo": photo_data})
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

            return redirect("/")
        return render_template("upload.html")

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

    @app.route("/status")
    def test_ml():
        res = request.get("http://ml-client:6000/status")
        print(res)

    return app


if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "3000")
    application = create_app()
    application.run(port=FLASK_PORT)
