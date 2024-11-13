"""
Web application for sound classification.

This Flask app provides a web interface for recording audio and displaying classification results.
"""

from flask import Flask, render_template


def launch_app():
    """Get the app launched"""
    app = Flask(__name__)  # pylint: disable=invalid-name

    @app.route("/")
    def index():
        """Render the index page."""
        return render_template("index.html")

    # @app.route('/results')
    # def results():
    #     return render_template('results.html')

    return app


if __name__ == "__main__":
    client_app = launch_app()
    client_app.run(host="0.0.0.0", port=5000)
