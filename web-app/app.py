from flask import Flask, render_template, request, redirect, url_for
from characterai import aiocai, pycai, sendCode, authUser
import asyncio
import pymongo
from pymongo import MongoClient

email = ''
code = ''
client = ''
db = None

def init_db():
    global db
    mongodb+srv://vernairesl:Iloveu325@cluster0.jy4go.mongodb.net/myapp?retryWrites=true&w=majority&appName=Cluster0
    db = mongo_client['myapp']

def create_app():
    app = Flask(__name__)
    init_db()
    
    @app.route('/', methods=['GET', 'POST'])
    def login():
        global email, code
        if request.method == 'POST':
            email = request.form['email']
            if not email:
                return "Email address is required", 400
            print(email)
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
