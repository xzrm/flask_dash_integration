from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
import os
# from project.config import DevelopmentConfig

server = Flask(__name__)
# server.config.from_object(DevelopmentConfig)
server.config.from_object('config.ProductionConfig')


db = SQLAlchemy(server, session_options={
    'expire_on_commit': False
})



login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.init_app(server)

admin = Admin(server)

mail = Mail()
mail.init_app(server)

from .models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

from .admin import *

###dash apps

# from werkzeug.middleware.dispatcher import DispatcherMiddleware
from .app_dash1 import dash_app1
from .app_dash2 import dash_app2


# app_dash = DispatcherMiddleware(server, {
#     '/dash': dash_app1.server
#     # '/app2': dash_app2.server,
# })

from project.users.routes import users
from project.projects.routes import projects
from project.main.routes import main

server.register_blueprint(users)
server.register_blueprint(projects)
server.register_blueprint(main)

# from project import routes