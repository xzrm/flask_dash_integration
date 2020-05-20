from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from passlib.hash import sha256_crypt

from project import db
from project.models import *
from project.users.forms import LoginForm, RegisterForm, UpdateAccountForm

users = Blueprint('users', __name__)

@users.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        default_role = Role.query.filter_by(name='superuser').first()
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
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print(current_user.name)
        return redirect(url_for('main.index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and sha256_crypt.verify(form.password.data, user.password):
                login_user(user)
                flash('You are logged in', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are successfully logged out', 'success')
    return redirect(url_for('users.login'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)