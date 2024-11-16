"""
A simple Flask web application for the machine-learning-client service.

This app provides a basic HTTP server with a single route that returns a greeting message.
It's primarily used to keep the container running for testing and service purposes.
"""


from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    """
    Home route that returns a greeting message.

    Returns:
        str: A simple greeting message.
    """
    return "<h1>Hello!<!h1>"


@app.route("/predict/<file_id>")
def predict(file_id):
    """
    Will handle the prediction based on file_id
    """
    return (
        jsonify(
            {
                "message": "Prediction request received",
                "file_id": file_id,
                "status": "OK",
            }
        ),
        200,
    )


if __name__ == "__main__":
    print("ML Client running on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
