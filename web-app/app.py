# import necessary pkgs
import flask
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import flask_login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import os

# instantiate flask app, create key
app = Flask(__name__)
app.secret_key = "tripledoubleholymoly"

# code for setting up flask login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# at some point we will need to connect to pymongo db
users = {'bob123': {'password': 'test'}, 'jen987': {'password': 'foobar'}}

class User(flask_login.UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    # catch error if user is not in database
    if username not in users:
        return
    
    # create new user object
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


@app.route("/login", methods = ['GET', 'POST'])
def login():
    if (flask.request.method == 'GET'):
        # pypi default, in future create template
        return '''
               <form action='login' method='POST'>
                <input type='text' name='username' id='username' placeholder='username'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    username = flask.request.form['username']
    if username in users and flask.request.form['password'] == users[username]['password']:
        user = User()
        user.id = username
        flask_login.login_user(user)
        return flask.redirect(url_for('show_home', username = username))

    return 'Bad login'

@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Uh oh! You are not authorized to access this account.', 401

# when app is launched, should be taken directly to login page
@app.route("/")
def redirect_login():
    return redirect(url_for('login'))


# protected page once user completes login
@app.route("/<username>")
@login_required
def show_home(username):
    return "Welcome, " + username + "!"
    # need to implement:
    #   - button to record, talk with team more about how pages will be organized
    #   - button to redirect to next page to show user's statistics

# @app.route("/<username>/mystats")
# @login_required
