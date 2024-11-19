"""
This module contains the Flask application for a web application
that provides user authentication and session management with MongoDB.
"""

import os
import time
from threading import Thread, Event
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
)
import pymongo
import certifi
from bson.objectid import ObjectId
from dotenv import load_dotenv



load_dotenv()


# Define an event to signal the function to stop
stop_event = Event()


def background_task():
    """
    A simple background task that runs in a loop until the stop event is set.
    """
    while not stop_event.is_set():
        print("Running background task...")
        time.sleep(1)  # Simulate work


def create_app():
    """
    Create and configure the Flask application.
    Returns:
        Flask: The Flask application object.
    """
    app = Flask(__name__)

    app.secret_key = os.getenv("SECRET_KEY")
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = cxn[os.getenv("MONGO_DBNAME")]

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    try:
        cxn.admin.command("ping")
        print(" * Connected to MongoDB!")
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(" * MongoDB connection error:", e)

    class User(UserMixin):
        """
        Represents a logged-in user.
        """

        def __init__(self, user_id):
            self.id = user_id

    @login_manager.user_loader
    def load_user(user_id):
        """
        Load the user object from the database by user ID.
        Args:
            user_id (str): The ID of the user.
        Returns:
            User: A User object if found, otherwise None.
        """
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(str(user_data["_id"]))
        return None

    @app.route("/", methods=["GET", "POST"])
    def login():
        """
        Route for the login page.
        """
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user_data = db.users.find_one({"username": username})

            if user_data and user_data["password"] == password:
                user = User(str(user_data["_id"]))
                login_user(user)
                return redirect(url_for("home_page"))
            flash("Invalid username or password.")

        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        """
        Route for the sign-up page.
        Allows new users to create an account and saves their information to the database.
        """
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            existing_user = db.users.find_one({"username": username})
            if existing_user:
                return redirect(url_for("signup"))

            new_user = {"username": username, "password": password}
            db.users.insert_one(new_user)

            return redirect(url_for("login"))

        return render_template("signup.html")

    @app.route("/home_page")
    @login_required
    def home_page():
        """
        Route for the home page.
        Returns:
            str: The rendered HTML template.
        """
        past_sessions = db.sessions.find({"username": current_user.id}).sort(
            "created_at", -1
        )
        return render_template(
            "home_page.html", past=past_sessions, username=current_user.id
        )

    @app.route("/start-session")
    def session_form():
        """
        Route for the home page.
        Returns:
            rendered template (str): The rendered HTML template.
        """
        return render_template("focus.html")

    @app.route("/start", methods=["POST"])
    def start_function():
        """
        Start the background function.
        """
        if stop_event.is_set():  # Reset the stop event if previously set
            stop_event.clear()

        thread = Thread(target=background_task, daemon=True)
        thread.start()
        return jsonify({"status": "started"}), 200


    @app.route("/stop", methods=["POST"])
    def stop_function():
        """
        Stop the background function.
        """
        stop_event.set()
        return jsonify({"status": "stopped"}), 200

    return app


if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    flask_app = create_app()
    flask_app.run(port=FLASK_PORT)
