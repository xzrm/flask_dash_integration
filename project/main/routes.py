from flask import Flask, render_template, redirect, Blueprint

from flask_login import login_required

main = Blueprint('main', __name__)




@main.route('/')
def index():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')
