"""
Flask application initialization module.
This module creates and configures the Flask application instance.
"""

from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# This import needs to be here to avoid circular imports
# pylint: disable=wrong-import-position,cyclic-import
from app import routes
