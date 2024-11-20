"""
Flask application with camera tracking integration using OpenCV and MongoDB.
"""

import os
import sys
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

# Add path for the machine-learning-client directory
sys.path.append(os.path.abspath("../machine-learning-client"))

# Import camera and mouse tracking functions with aliases
try:
    from camera_tracker import (
        start_tracking as start_camera_tracking,
        stop_tracking as stop_camera_tracking,
    )
    from mouse_tracker import (
        start_tracking as start_mouse_tracking,
        stop_tracking as stop_mouse_tracking,
    )
except ImportError as e:
    print(f"ImportError: {e}")

load_dotenv()


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
        print(f" * MongoDB connection error: {e}")

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
                flash("Username already exists. Please choose a different username.")
                return redirect(url_for("signup"))

            new_user = {"username": username, "password": password}
            db.users.insert_one(new_user)

            flash("Account created successfully. Please log in.")
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
        Render the focus session control page.
        """
        return render_template("focus.html")

    @app.route("/start", methods=["POST"])
    def start_tracking_route():
        """
        Start both camera and mouse tracking.
        """
        try:
            # Uncomment these lines if camera tracking is needed
            start_camera_tracking()

            start_mouse_tracking()
            return jsonify({"status": "tracking_started"}), 200
        except pymongo.errors.PyMongoError as db_error:
            return (
                jsonify({"status": "error", "message": f"Database error: {db_error}"}),
                500,
            )
        except ValueError as value_error:
            return (
                jsonify({"status": "error", "message": f"Value error: {value_error}"}),
                500,
            )
        except RuntimeError as runtime_error:
            return (
                jsonify(
                    {"status": "error", "message": f"Runtime error: {runtime_error}"}
                ),
                500,
            )

    @app.route("/stop", methods=["POST"])
    def stop_tracking_route():
        """
        Stop both camera and mouse tracking.
        """
        try:
            # Uncomment these lines if camera tracking is needed
            stop_camera_tracking()

            stop_mouse_tracking()
            return jsonify({"status": "tracking_stopped"}), 200
        except pymongo.errors.PyMongoError as db_error:
            return (
                jsonify({"status": "error", "message": f"Database error: {db_error}"}),
                500,
            )
        except Exception as general_error:  # pylint: disable=broad-exception-caught
            # Broad exception to catch unexpected errors and prevent crashes.
            return jsonify({"status": "error", "message": str(general_error)}), 500

    return app


if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    flask_app = create_app()
    flask_app.run(port=FLASK_PORT)
