import os
import pymongo
from flask import Flask

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongo_uri)
db = client["sensor_data"]


@app.route("/")
def index():
    return "Connected to MongoDB: {}".format(db.name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
