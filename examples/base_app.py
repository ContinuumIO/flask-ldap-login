from flask_login import LoginManager, login_user
from flask import Flask, request, render_template, redirect


app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

app.secret_key = 'creative cat'
login_manager = LoginManager(app)

users = {}

class User(object):
    def __init__(self, username, data=None):
        self.username = username
        self.data = data

    def __repr__(self):
        return '<User %r %r>' % (self.username, self.data)
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(userid):
    return users.get(userid)

