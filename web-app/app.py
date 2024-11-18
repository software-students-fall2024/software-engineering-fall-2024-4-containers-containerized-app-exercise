"""
Web application for managing the boyfriend AI client.
"""

import os
from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["boyfriend_db"]
collection = db["focus_data"]

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)
