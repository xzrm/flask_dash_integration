from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

server = Flask(__name__)

server.secret_key = "secret"
server.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:334hprkT@localhost/dash_projects_dev"
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(server, session_options={
    'expire_on_commit': False
})



login_manager = LoginManager()
login_manager.init_app(server)

admin = Admin(server)


from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

from .admin import *

###dash apps

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from .app_dash1 import dash_app1
# from .app_dash2 import app as dash_app2


app_dash = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server
    # '/app2': dash_app2.server,
})

from project import routes