"""
Web application routes module.
This module defines all the routes and their handling logic.
"""

from flask import render_template, request
from app import app
from app.models import Database


@app.route("/")
def index():
    """Render the main page of the application."""
    return render_template("index.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """
    Handle dashboard page requests.
    GET: Display the dashboard with history
    POST: Process uploaded image and show results
    """
    db = Database()
    result = None
    if request.method == "POST" and "image" in request.files:
        # Image processing logic will be added here
        pass
    history = db.get_latest_results()
    return render_template("dashboard.html", result=result, history=history)
