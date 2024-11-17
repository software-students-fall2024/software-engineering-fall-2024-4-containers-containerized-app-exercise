"""ML Client Flask Application.

This module sets up a simple Flask application that provides endpoints
to interact with machine learning services.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/status", methods=["GET"])
def status():
    """Check the status of the ML Client.

    Returns:
        tuple: A tuple containing a JSON response and an HTTP status code.
    """
    return jsonify({"message": "ML Client is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)