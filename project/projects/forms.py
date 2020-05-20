from wtforms import StringField, TextAreaField, SelectField, validators, SubmitField
from flask_wtf import FlaskForm

class ProjectForm(FlaskForm):
    title = StringField('Title', [validators.DataRequired()])
    description = StringField('Description', [validators.Length(min=1, max=250)])
    category = SelectField('Category', [validators.DataRequired()], choices=[('conv','convergence behaviour')])
    submit = SubmitField('Create')
    
    