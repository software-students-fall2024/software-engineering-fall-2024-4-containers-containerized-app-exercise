import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for
from characterai import aiocai, pycai, sendCode, authUser
import asyncio
import pymongo
from bson import ObjectId
import certifi

email = ''
code = ''
client = ''

def create_app():

    load_dotenv()

    mongo_uri = os.getenv("MONGO_DB_URI")

    if mongo_uri is None:
        raise ValueError("Could not connect to database. Make sure .env is properly configured.")
    
    mongo_cli = pymongo.MongoClient(mongo_uri, tls=True, tlsCAFile=certifi.where())

    try:
        mongo_cli.admin.command('ping')  
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

    db = mongo_cli['hellokittyai_db']
    users = db['users']
    characters = db['characters']
    chats = db['chats']

    app = Flask(__name__)
    
    @app.route('/', methods=['GET', 'POST'])
    def login():
        global email, code
        if request.method == 'POST':
            email = request.form['email']
            if not email:
                return "Email address is required", 400
            
            user = users.find_one({"email": email})
            if not user:
                user_id = str(ObjectId())
                users.insert_one({"user_id": user_id, "email": email, "chat_history": []})
                print(f"New user created: {email}")
            code = sendCode(email)
            return render_template('auth.html', address=email)
        
        return render_template('index.html')

    @app.route('/authenticate', methods=['POST'])
    def auth():
        global client
        link = request.form['link']
        print(f"Email: {email}, Link: {link}, Code: {code}")
        token = authUser(link, email)
        client = pycai.Client(token)

        return redirect(url_for('home'))

    @app.route('/home', methods=['GET'])
    def home():
        cli = client.get_me()
        return render_template('home.html', address=email, info=cli)

    return app

if __name__ == "__main__":
    web_app = create_app()
    web_app.run(port=8000)
