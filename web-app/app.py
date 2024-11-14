"""
Flask web application for Trackly
"""

import os
from flask import Flask, render_template
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()

def create_app():

    """
    Configure Flask Application
    Returns: Flask App
    """

    app = Flask(__name__)

    mongo_uri = os.getenv("MONGO_URI")

    if mongo_uri is None:
        raise ValueError("Error with URI")

    try:
        client = MongoClient(mongo_uri)
        db = client.get_database("Trackly")
        app.db = db
        #collection = db["entries"]
        print("Connected to MongoDB")
    except errors.ServerSelectionTimeoutError as con_e:
        print(f"Error connecting to MongoDB Database: {con_e}")
        app.db =  None
    except errors.ConfigurationError as fig_e:
        print(f"Error configuring MongoDB Database: {fig_e}")
        app.db = None

    @app.route("/")
    def home():
        """
        Serves home page
        """
        return render_template("home.html")

    return app

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    flask_app = create_app()
    flask_app.run(port=FLASK_PORT)
