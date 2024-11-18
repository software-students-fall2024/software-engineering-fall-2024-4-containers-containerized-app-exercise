"""
Flask app for Hello Kitty AI application.
Handles user authentication, connection to MongoDB, and basic routes.
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from characterai import pycai, sendCode, authUser
import pymongo
from bson import ObjectId
import certifi


# Global variables
EMAIL = ""
CODE = ""
CLIENT = None


def create_app():
    """Creates and configures the Flask application."""
    load_dotenv()

    mongo_uri = os.getenv("MONGO_DB_URI")
    if mongo_uri is None:
        raise ValueError("Could not connect to database. Ensure .env is properly configured.")

    mongo_cli = pymongo.MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())

    try:
        mongo_cli.admin.command("ping")
        print("Successfully connected to MongoDB!")
    except pymongo.errors.PyMongoError as error:
        print(f"Failed to connect to MongoDB: {error}")

    db = mongo_cli["hellokittyai_db"]
    users = db["users"]

    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def login():
        """
        Handles user login and code sending.
        Creates a new user if they don't exist.
        """
        global EMAIL, CODE

        if request.method == "POST":
            email = request.form.get("email")
            if not email:
                return "Email address is required", 400

            EMAIL = email
            user = users.find_one({"email": EMAIL})
            if not user:
                user_id = str(ObjectId())
                users.insert_one({"user_id": user_id, "email": EMAIL, "chat_history": []})
                print(f"New user created: {EMAIL}")

            CODE = sendCode(EMAIL)
            return render_template("auth.html", address=EMAIL)

        return render_template("index.html")

    @app.route("/authenticate", methods=["POST"])
    def auth():
        """
        Authenticates the user using the link provided and saves the client instance.
        """
        global CLIENT
        link = request.form.get("link")
        if not link:
            return "Authentication link is required", 400

        print(f"Email: {EMAIL}, Link: {link}, Code: {CODE}")
        token = authUser(link, EMAIL)
        CLIENT = pycai.Client(token)

        return redirect(url_for("home"))

    @app.route("/home", methods=["GET"])
    def home():
        """Displays the user's home page with their information."""
        if not CLIENT:
            return "Client is not authenticated. Please log in.", 403

        cli = CLIENT.get_me()
        return render_template("home.html", address=EMAIL, info=cli)

    return app

if __name__ == "__main__":
    web_app = create_app()
    web_app.run(port=8000)
