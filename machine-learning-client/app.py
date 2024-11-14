"""
A simple Flask web application for the machine-learning-client service.

This app provides a basic HTTP server with a single route that returns a greeting message.
It's primarily used to keep the container running for testing and service purposes.
"""


from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    """
    Home route that returns a greeting message.

    Returns:
        str: A simple greeting message.
    """
    return "<h1>Hello!<!h1>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
