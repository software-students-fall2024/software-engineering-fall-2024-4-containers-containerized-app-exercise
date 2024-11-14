"""
This is the Flask web application that serves as the interface for
the machine learning model.
"""

from flask import Flask, render_template, request, jsonify


def create_app():
    """
    Create and configure the Flask application
    Returns: app: the Falsk application object
    """
    app = Flask(__name__)
    print("hello world!")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/record",methods=["POST"])
    def record():
        audio_data = request.files["audio"]
        if audio_data:
            response = requests.post("http://ml-client:5000/transcribe", files={'audio': audio_data})
            return jsonify({'status': 'success','text':'trial successfully!'})
        else:
            return jsonify({'status': 'error'})
    return app


if __name__ == "__main__":
    web_app = create_app()
    web_app.run(host="0.0.0.0")
