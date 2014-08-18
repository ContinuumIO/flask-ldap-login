'''
Base flask application to use in ldap examples
'''
from flask_login import LoginManager
from flask import Flask, render_template


app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

app.secret_key = 'creative cat'
login_manager = LoginManager(app)

# Store users in memory
users = {}

class User(object):
    'Simple user object for use with flask-login'
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

