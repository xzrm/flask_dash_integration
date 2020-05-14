from project import db
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flask_security import RoleMixin
from flask_login import UserMixin

from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON


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
    category = db.Column(db.String, nullable=False)
    create_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    results = db.relationship("Result", uselist=False, lazy='subquery', back_populates="project")
    

    def __init__(self, title, description, author_id, category):
        self.title = title
        self.description = description
        self.author_id = author_id
        self.category = category

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
    projects = db.relationship("Project", secondary=users_projects, 
                            backref="users", lazy='subquery')

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
    
    
class Result(db.Model):
    
    __tablename__ = "result"
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    project = db.relationship("Project", back_populates="results")
    data = db.relationship("Data", backref="results", lazy='subquery')
    
    def __init__(self, project):
        self.project = project
    

class Data(db.Model):
    
    __tablename__ = "data"
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'))
    data = db.Column(JSON)
    
    # def __init__(self, data):
    #     self.data = data
        
    