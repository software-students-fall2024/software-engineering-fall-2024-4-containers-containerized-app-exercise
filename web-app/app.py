"""
This is the Flask web application that serves as the interface for
the machine learning model.
"""
from flask import Flask
def create_app():
    """
    Create and configure the Flask application
    Returns: app: the Falsk application object
    """
    app = Flask(__name__)
    print("hello world!")
    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
