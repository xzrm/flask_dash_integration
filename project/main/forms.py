from wtforms import StringField, TextAreaField, SelectField, validators, SubmitField
from flask_wtf import FlaskForm

class ContactForm(FlaskForm):
    
    name = StringField('Name', [validators.DataRequired()])
    email = StringField(
        'Email', [validators.DataRequired(), validators.Email()])
    subject = StringField('Subject', [validators.DataRequired()])
    message = TextAreaField('Message', [validators.Length(min=1, max=300)])
    submit = SubmitField('Send')