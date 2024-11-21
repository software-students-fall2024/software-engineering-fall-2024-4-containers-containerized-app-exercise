"""
Module: a flask application that acts as the interface for user login,
audio recording, and viewing statistics
"""

from flask import Flask, render_template, request, redirect, url_for
import flask_login
from flask_login import login_user, login_required, logout_user

# instantiate flask app, create key
app = Flask(__name__)
app.secret_key = "tripledoubleholymoly"

# setup flask-login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# simulated database of users, need to implement
users = {"bob123": {"password": "test"}, "jen987": {"password": "foobar"}}


class User(flask_login.UserMixin):  # pylint: disable = too-few-public-methods
    """user class for flask-login"""

    def __init__(self, username: str) -> None:
        self.id = username


@login_manager.user_loader
def user_loader(username):
    """load a user by their username"""
    if username not in users:
        return None
    user = User(username)
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    """handles login functionality"""
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # validate input
        if not username or not password:
            error = "Error: Missing username or password"

        elif username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user)

            return redirect(url_for("show_home", username=username))
        else:
            error = "Error: Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    """handles account creation interface and functionality"""
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # validation logic
        if username in users:
            error = "Error: Username already exists, try another!"
        elif not username or not password:
            error = "Error: Username or password left blank."
        elif password != password_confirm:
            error = "Error: Passwords do not match."
        else:
            # Add new user to "database"
            users[username] = {"password": password}
            return redirect(url_for("login"))

    return render_template("create_account.html", error=error)


@app.route("/logout")
def logout():
    """handles user logout"""
    logout_user()

    return redirect(url_for("login"))


@login_manager.unauthorized_handler
def unauthorized_handler():
    """handles situation during unauthorized access"""
    return "Unauthorized Access. Please log in.", 401


@app.route("/")
def redirect_login():
    """redirect to login page"""

    return redirect(url_for("login"))


@app.route("/<username>")
@login_required
def show_home(username):
    """show logged-in user's homepage"""

    return render_template("user_home.html", username=username)
