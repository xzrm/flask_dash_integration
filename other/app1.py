from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, abort
from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_wtf import Form
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
# from flask_login import login_user, login_required, logout_user
from passlib.hash import sha256_crypt
from functools import wraps

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
# from app import bcrypt
from passlib.hash import sha256_crypt


from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from dash import Dash
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import dash_html_components as html
import dash_core_components as dcc

# from flask_security import Security, SQLAlchemyUserDatastore, \
#     UserMixin, RoleMixin, login_required, current_user

from flask_security import RoleMixin
from flask_login import LoginManager, login_user, UserMixin,\
                        logout_user, current_user, login_required

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)



app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:334hprkT@localhost/dash_projects_dev"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

from app_dash1 import app as dash_app1
from app_dash2 import app as dash_app2


@app.route('/chart1/')
@login_required
def render_chart1():
    return redirect('/app1')


@app.route('/chart2/')
@login_required
def render_chart2():
    return redirect('/app2')

app_dash = DispatcherMiddleware(app, {
    '/app1': dash_app1.server,
    '/app2': dash_app2.server,
})

### models 
users_projects = db.Table('users_projects',
        db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
        db.Column('project_id', db.Integer, db.ForeignKey('projects.id')),
)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    
    __tablename__ = 'role'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

class Project(db.Model):

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String, nullable=False)
    description= db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, title, description):
        self.title = title
        self.description = description

    def __repr__(self):
        return '<{}>'.format(self.title)


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    roles = db.relationship('Role', secondary=roles_users,
                            backref="users", lazy='select')
    projects = relationship("Project", secondary=users_projects, 
                            backref="users", lazy='select')

    def __init__(self, name, email, username, password, roles):
        self.name = name
        self.email = email
        self.username = username
        self.password = sha256_crypt.encrypt(str(password))
        self.roles = roles
          
    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})
 
    def __repr__(self):
        return '<name - {}>'.format(self.name)

# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)

# from models import *
admin = Admin(app)


### logic
class MyModelView(ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('login'))


    # can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True


admin.add_view(MyModelView(Project, db.session))
admin.add_view(MyModelView(User, db.session))

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
@login_required
def projects():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    projects = user.projects
    return render_template('projects.html', projects=projects)


@app.route('/projects/<string:id>/')
@login_required
def project(id):
    project = Project.query.filter_by(id=id).first()
    return render_template('project.html', project=project)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=25)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')
    
class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    
class ProjectForm(Form):
    title = StringField('Title', [validators.DataRequired()])
    description = StringField('Description', [validators.Length(min=1, max=250)])
    
@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('You are successfully registered.', 'success')
        # login_user(user)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(current_user.name)
        return redirect(url_for('index'))
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            user = User.query.filter_by(name=request.form['username']).first()
            if user is not None and sha256_crypt.verify(request.form['password'], user.password):
                # session['logged_in'] = True
                # session['username'] = user.username
                login_user(user)
                print(current_user.name)
                flash('You are logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid credentials'
                return render_template('login.html', error=error)
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    # print(session)
    # session.clear()
    logout_user()
    flash('You are successfully logged out', 'success')
    return redirect(url_for('login'))
    



if __name__ == '__main__':
    # app.run(debug=True)
    run_simple('localhost', 5000, app_dash, use_reloader=True, use_debugger=True)
