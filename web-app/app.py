import os
from flask import Flask, render_template, jsonify, request, redirect, url_for
from characterai import aiocai, pycai, sendCode, authUser
from pymongo import MongoClient, errors


MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['boyfriend_db']
collection = db['focus_data']    
email = ''


app = Flask(__name__)


if __name__ == "__main__":
    app.run(debug=True)
