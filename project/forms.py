from wtforms import Form, StringField, TextAreaField, \
    PasswordField, SelectField, validators

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
    category = SelectField('Category', [validators.DataRequired()], choices=[('conv','convergence behaviour')])
    # category = language = SelectField(u'Category', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    
    