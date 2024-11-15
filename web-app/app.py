"""
A simple Flask application.
This module sets up a basic web server using Flask.
"""

from flask import Flask, render_template, jsonify

# Initialize the Flask app
app = Flask(__name__)


# Define a route for the homepage
@app.route("/")
def home():
    """Returns the index.html file."""
    return render_template("index.html")


# Define a route for the tutorial page
@app.route("/tutorial")
def tutorial():
    """Returns the tutorial.html file."""
    return render_template("tutorial.html")


# Define a route for the game page
@app.route("/game")
def game():
    """Returns the game.html file."""
    return render_template("game.html")


# Define another sample route for JSON data
@app.route("/data")
def data():
    """Returns a JSON of the data."""
    sample_data = {
        "name": "Dockerized Flask App",
        "description": "This is a Flask app running inside Docker.",
    }
    return jsonify(sample_data)


# Run the app only if this file is executed directly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Host set to '0.0.0.0' for Docker compatibility
