from project import db
from project.models import *

# insert data
db.drop_all()
db.create_all()

user_role = Role(name='user')
super_user_role = Role(name='superuser')
db.session.add(user_role)
db.session.add(super_user_role)

# commit the changes
db.session.commit()