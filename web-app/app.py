# import necessary pkgs
import flask
from flask import Flask, render_template, request, redirect, url_for
import flask_login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# instantiate flask app, create key
app = Flask(__name__)
app.secret_key = "tripledoubleholymoly"

# Setup flask-login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# Simulated database of users
users = {'bob123': {'password': 'test'}, 'jen987': {'password': 'foobar'}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    # Fetch user from "database"
    if username not in users:
        return None
    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return
    
    user = User()
    user.id = username
    return user

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate input
        if not username or not password:
            error = "Error: Missing username or password"
        elif username in users and users[username]['password'] == password:
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('show_home', username=username))
        else:
            error = "Error: Invalid credentials"

    return render_template('login.html', error=error)

@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Validation logic
        if username in users:
            error = "Error: Username already exists, try another!"
        elif not username or not password:
            error = "Error: Username or password left blank."
        elif password != password_confirm:
            error = "Error: Passwords do not match."
        else:
            # Add new user to "database"
            users[username] = {'password': password}
            return redirect(url_for('login'))

    return render_template('create_account.html', error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return "Unauthorized Access. Please log in.", 401

@app.route("/")
def redirect_login():
    return redirect(url_for('login'))

@app.route("/<username>")
@login_required
def show_home(username):
    return render_template("user_home.html", username = username)
