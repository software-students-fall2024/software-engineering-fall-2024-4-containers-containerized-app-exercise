"""
This is the Flask web application that serves as the interface for
the machine learning model.
"""

from flask import Flask, render_template


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

    return app


if __name__ == "__main__":
    web_app = create_app()
    web_app.run(host="0.0.0.0")
