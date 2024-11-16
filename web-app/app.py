from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from pymongo import MongoClient
from os import getenv
from hashlib import sha256
from bson import ObjectId 


connstr = getenv("DB_URI")
key = getenv("SECRET")

if connstr is None:
    raise Exception("Database URI could not be loaded: check .env file")

if key is None:
    raise Exception("Flask secret could nto be loaded: check .env file")

app = Flask(__name__)
app.secret_key = key


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = MongoClient(connstr)

collection = db['TODO']['users']


'''
user document
{
    username: string unique
    password_hash: string 
}
'''

class UserSchema(UserMixin):
    def __init__(self, username, password=None):
        self.username = username
        self.password_hash = self.hash_password(password) if password else ""
        self.id = None

    def hash_password(self, password):
        return sha256(password.encode()).hexdigest()

    def to_dict(self):
        return {
            'username': self.username,
            'password_hash': self.password_hash,
        }

    @staticmethod
    def get_user(username):
        user = collection.find_one({'username': username})
        if not user:
            return None

        record = UserSchema(user['username'])
        record.password_hash = user['password_hash']
        record.id = str(user['_id'])
        return record


    def insert_record(self):
        user = collection.find_one({'username': self.username})
        if user is not None:
            raise Exception("username already exists")
        user = collection.insert_one(self.to_dict())



@login_manager.user_loader
def load_user(user_id):
    user = collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return None
    return UserSchema.get_user(user['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    password = request.form['password']

    try:
        new_user = UserSchema(username, password)
        new_user.insert_record()
        return redirect(url_for('login'))
    except Exception as e:
        return str(e)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    user = UserSchema.get_user(username)
    if user:
        if user.hash_password(password) == user.password_hash:
            session['username'] = username
            login_user(user)  # Log the user in
            return redirect(url_for('list_tasks'))
        else:
            return "Invalid password"
    return "Invalid username"

@app.route('/logout')
def logout():
    print('hit')
    logout_user()
    return redirect(url_for('login'))

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return redirect(url_for('login'))



if __name__ == '__main__':
    print("App listening on port 8080")
    app.run(host="0.0.0.0", port=8080)
