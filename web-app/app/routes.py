"""
Web application routes module.
This module defines all the routes and their handling logic.
"""

from flask import render_template, request, redirect, url_for, flash, session
from app import app
from app.models import Database
from werkzeug.security import generate_password_hash, check_password_hash


@app.route("/")
def index():
    """Render the main page of the application."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        db = Database()
        user = db.find_user({"email": email})
        
        if user and check_password_hash(user["password"], password):
            session["user"] = email
            return redirect(url_for("dashboard"))
        flash("Invalid email or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        db = Database()
        if db.find_user({"email": email}):
            flash("Email already exists")
            return redirect(url_for("register"))
            
        hashed_password = generate_password_hash(password)
        db.add_user({
            "email": email,
            "password": hashed_password
        })
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    """Handle user logout"""
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    Handle dashboard page requests.
    Requires user authentication.
    """
    if "user" not in session:
        return redirect(url_for("login"))
        
    db = Database()
    result = None
    if request.method == "POST" and "image" in request.files:
        # Image processing logic will be added here
        pass
    history = db.get_latest_results()
    return render_template("dashboard.html", result=result, history=history)
