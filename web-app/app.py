"""
Flask app for Hello Kitty AI application.
Handles user authentication, connection to MongoDB, and basic routes.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv
from characterai import pycai, sendCode, authUser
import pymongo
from bson import ObjectId
import certifi


def create_app():
    """Creates and configures the Flask application."""
    load_dotenv()

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY not found. Add it to your .env file.")

    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri is None:
        raise ValueError(
            "Could not connect to database. Ensure .env is properly configured."
        )

    mongo_cli = pymongo.MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())

    try:
        mongo_cli.admin.command("ping")
        print("Successfully connected to MongoDB!")
    except pymongo.errors.PyMongoError as error:
        print(f"Failed to connect to MongoDB: {error}")

    db = mongo_cli["hellokittyai_db"]
    users = db["users"]

    app = Flask(__name__)
    app.secret_key = secret_key

    @app.route("/", methods=["GET", "POST"])
    def login():
        """
        Handles user login and code sending.
        Creates a new user if they don't exist.
        """
        if request.method == "POST":
            email = request.form.get("email")
            if not email:
                return "Email address is required", 400

            session["email"] = email
            user = users.find_one({"email": email})
            if not user:
                user_id = str(ObjectId())
                users.insert_one(
                    {"user_id": user_id, "email": email, "chat_history": []}
                )
                print(f"New user created: {email}")

            session["code"] = sendCode(email)
            return render_template("auth.html", address=email)

        return render_template("index.html")

    @app.route("/authenticate", methods=["POST"])
    def auth():
        """
        Authenticates the user using the link provided and saves the client instance.
        """
        link = request.form.get("link")
        if not link:
            return "Authentication link is required", 400

        email = session.get("email")
        code = session.get("code")
        if not email or not code:
            return "Session expired. Please log in again.", 403

        print(f"Email: {email}, Link: {link}, Code: {code}")
        token = authUser(link, email)
        session["token"] = token

        return redirect(url_for("home"))

    @app.route("/home", methods=["GET"])
    def home():
        """Displays the user's home page with their information."""
        token = session.get("token")
        if not token:
            return "Client is not authenticated. Please log in.", 403
        return render_template("home.html", address=session.get("email"))

    @app.route("/chat", methods=["GET", "POST"])
    def chat_with_character():
        """Handles chatting with a specific character."""
        character_id = "7xhfgdiu2oj2NIRnQQRx42Q2cwr0sFIRu7xZeRZYWn0"

        if request.method == "GET":
            return render_template("chat.html")

        token = session.get("token")
        if not token:
            return (
                jsonify({"error": "Client is not authenticated. Please log in."}),
                403,
            )

        client = pycai.Client(token)
        me = client.get_me()

        with client.connect() as chat:
            new= chat.new_chat(character_id, me.id)

            user_message = request.get_json().get("message")
            response = chat.send_message(character_id, new.chat_id, user_message)

        return jsonify(
            {
                "character_name": response.name,
                "character_message": response.text,
            }
        )

    return app


if __name__ == "__main__":
    web_app = create_app()
    web_app.run(port=8000)
