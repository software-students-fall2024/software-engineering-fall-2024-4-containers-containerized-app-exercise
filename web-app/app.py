import os
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, jsonify, render_template, request, redirect, abort, url_for, make_response, send_from_directory,session

load_dotenv()
app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)



if __name__ == "__main__":
    app.run(debug=True)