from flask import Flask, request, render_template, flash, redirect, url_for, session, logging, abort
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt


from flask_security import RoleMixin
from flask_login import LoginManager, login_user, UserMixin,\
                        logout_user, current_user, login_required

from .forms import RegisterForm, LoginForm, ProjectForm
from project import server, db, login_manager, admin
from .models import *


# from .app_dash1 import app as dash_app1
# from .app_dash2 import app as dash_app2


@server.route('/app1/')
@login_required
def render_chart():
    return redirect('/dash1')

# @server.route('/chart2/')
# @login_required
# def render_chart2():
#     return redirect('/app2')

@server.route('/projects/<string:id>/')
@login_required
def project(id):
    # project = Project.query.filter_by(id=id).first()
    session["project_id"] = id
    return redirect(url_for('render_chart'))


@server.route('/')
def index():
    return render_template('home.html')

@server.route('/about')
def about():
    return render_template('about.html')


@server.route('/projects')
@login_required
def projects():
    username = current_user.username
    user = User.query.filter_by(username=username).first()
    projects = user.projects
    return render_template('projects.html', projects=projects)


# @server.route('/projects/<string:id>/')
# @login_required
# def project(id):
#     project = Project.query.filter_by(id=id).first()
#     return render_template('project.html', project=project)


@server.route('/projects/new', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            author_id = current_user.id,
            category=form.category.data
        )
        db.session.add(project)
        
        user = User.query.filter_by(username=current_user.username).first()
        user.projects.append(project)
        db.session.commit()
        print(user.projects)
        flash('You successfully added a project.', 'success')
        return redirect(url_for('projects'))
    return render_template('add_project.html', form=form)

    
@server.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        default_role = Role.query.filter_by(name='user').first()
        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            roles= [default_role, ]
        )
        db.session.add(user)
        db.session.commit()
        flash('You are successfully registered.', 'success')
        # login_user(user)
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@server.route('/login', methods=['GET', 'POST'])
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
                login_user(user)
                flash('You are logged in', 'success')
                return redirect(url_for('index'))
            else:
                error = 'Invalid credentials'
                return render_template('login.html', error=error)
    return render_template('login.html', error=error)

@server.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are successfully logged out', 'success')
    return redirect(url_for('login'))
    
    


