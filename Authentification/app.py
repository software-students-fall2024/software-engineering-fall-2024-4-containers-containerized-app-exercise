from flask import Flask, request, render_template, redirect, url_for, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "iygihdiwedweiweuodweneo"

# MongoDB configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)
db = mongo.db

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("signup"))

        if db.users.find_one({"username": username}):
            flash("User already exists.", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        db.users.insert_one({"username": username, "password": hashed_password})

        flash("User created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("login"))

        user = db.users.find_one({"username": username})
        if not user or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        flash("Login successful!", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
