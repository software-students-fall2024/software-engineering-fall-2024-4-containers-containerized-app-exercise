"""
A simple Flask web application for the machine-learning-client service.

This app provides a basic HTTP server with a single route that returns a greeting message.
It's primarily used to keep the container running for testing and service purposes.
"""


from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home():
    """
    Home route that returns a greeting message.

    Returns:
        str: A simple greeting message.
    """
    return "<h1>Hello!<!h1>"


@app.route("/predict")
def predict():
    """
    Will handle the prediction based on file_id
    """
    file_id = request.args.get("file_id")  # Retrieve file_id from query parameters
    if not file_id:
        return jsonify({"error": "file_id is required"}), 400

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
    print("ML Client running on port 5050")
    app.run(host="0.0.0.0", port=5050, debug=True)
