from flask_testing import TestCase

from project import server, db
from project.models import User, Project, Role


class BaseTestCase(TestCase):
    """A base test case."""

    def create_app(self):
        server.config.from_object('config.TestConfig')
        return server

    def setUp(self):
        db.create_all()
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        user = User("admin", "ad@min.com", "admin", "haslo", [user_role,])
        db.session.add(user)
        db.session.add(
            Project("Test project", "This is a test. Only a test.", user.id, 'convergence behaviour'))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()