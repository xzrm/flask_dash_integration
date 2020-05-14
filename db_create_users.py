from app import db
from models import User

# insert data
db.session.add(User("admin", "admin@email.com", "admin"))
db.session.add(User("user1", "user1@email.com", "haslo1"))
db.session.add(User("user2", "user2@email.com", "haslo2"))
db.session.add(User("user3", "user3@email.com", "haslo3"))


# commit the changes
db.session.commit()