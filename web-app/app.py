import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user 
import pymongo
import certifi

from bson.objectid import ObjectId 
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

def create_app():
    """
    Create and configure the Flask application.
    returns: app: the Flask application object
    """

    app = Flask(__name__)

    app.secret_key = os.getenv("SECRET_KEY")
    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
    db = cxn[os.getenv("MONGO_DBNAME")]

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'


    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)

    
    class User(UserMixin):
        pass

    @login_manager.user_loader
    def load_user(user_id):
        user_data = db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user = User()
            user.id = str(user_data['_id'])
            return user
        return None

    @app.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user_data = db.users.find_one({"username": username})

            if user_data and user_data['password'] == password: 
                user = User()
                user.id = str(user_data['_id'])
                login_user(user)
                return redirect(url_for('home_page'))
            else:
                flash('Invalid username or password.')

        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """
        Route for the sign-up page.
        Allows new users to create an account and saves their information to the database.
        """
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            existing_user = db.users.find_one({"username": username})
            if existing_user:
                return redirect(url_for('signup'))
            
            new_user = {
                "username": username,
                "password": password 
            }
            db.users.insert_one(new_user)

            return redirect(url_for('login'))

        return render_template('signup.html')

    @app.route("/home_page")
    @login_required
    def home_page():
        """
        Route for the home page.
        Returns:
            rendered template (str): The rendered HTML template.
        """

        past_sessions = db.sessions.find({"username": current_user.id}).sort("created_at", -1)

        return render_template("home_page.html", past=past_sessions, username=current_user.id)
    
    
    




        
        
    



    return app

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app = create_app()
    app.run(port=FLASK_PORT)