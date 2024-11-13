"""
This is a web app module for Attendify
"""

import os
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename  
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

db = client["test_db"]
users_collection = db["users"]
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def login_required(f):
    """to log in"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def home():
    """to handles the home route."""
    username = session.get("username")
    return render_template("home.html", username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """for users to sign up"""
    if request.method == "POST":
        try:
            username = request.form["username"]
            password = request.form["password"]
            image = request.files.get("image")

            if not username or not password or not image:
                return "Missing required fields", 400

            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)

            hashed_password = generate_password_hash(password)

            # simulate the face encoding (mocked response)
            face_encoding = [0.1, 0.2, 0.3, 0.4, 0.5]

            users_collection.insert_one(
                {
                    "username": username,
                    "password": hashed_password,
                    "image_path": image_path,
                    "encoding": face_encoding,
                }
            )
            return redirect(url_for("login"))

        except (KeyError, ValueError) as e:
            print(f"Error during signup: {str(e)}")
            return "Internal Server Error", 500

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """for users to log in"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("home"))
        return "Invalid username or password"

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """for users to log out"""
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
