import unittest

from flask_login import current_user
from flask import request

from base import BaseTestCase
from passlib.hash import sha256_crypt
from project.models import User


class TestUser(BaseTestCase):

    # Ensure user can register
    def test_user_registeration(self):
        with self.client:
            response = self.client.post('/register/', data=dict(
                name='Maciej', email='maciej@email.com',
                username='Maciek123', password='python',
                confirm_password='python'
            ), follow_redirects=True)
            self.assertIn(b'You are successfully registered.', response.data)
            
            user = User.query.filter_by(email='maciej@email.com').first()
            self.assertTrue(str(user) == '<name - Maciej>')

    # Ensure errors are thrown during an incorrect user registration
    def test_incorrect_user_registeration(self):
        with self.client:
            response = self.client.post('/register/', data=dict(
                name='Maciej', email='maciej@email.com',
                username='Maciek123', password='python',
                confirm_password='python123'
            ), follow_redirects=True)
            self.assertIn(b'Passwords do not match', response.data)
            self.assertIn('/register/', request.url)

    # Ensure id is correct for the current/logged in user
    def test_get_by_id(self):
        with self.client:
            self.client.post('/login', data=dict(
                email="ad@min.com", password="haslo"
            ), follow_redirects=True)
            self.assertTrue(current_user.id == 1)
            self.assertFalse(current_user.id == 20)

    # Ensure given password is correct after unhashing
    def test_check_password(self):
        user = User.query.filter_by(email='ad@min.com').first()
        self.assertTrue(sha256_crypt.verify(user.password, 'haslo'))
        self.assertFalse(sha256_crypt.verify(user.password, 'foobar'))


class UserViewsTests(BaseTestCase):

    # Ensure that the login page loads correctly
    def test_login_page_loads(self):
        response = self.client.get('/login')
        self.assertIn(b'Log In', response.data)

    # Ensure login behaves correctly with correct credentials
    def test_correct_login(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(email="ad@min.com", password="haslo"),
                follow_redirects=True
            )
            self.assertIn(b'You are logged in', response.data)
            self.assertTrue(current_user.name == "admin")
            self.assertTrue(current_user.is_active)

    #Ensure login behaves correctly with incorrect credentials
    def test_incorrect_login(self):
        response = self.client.post('/login', 
                                    data=dict(email="user1@email.com", password="haslo"),
                                    follow_redirects=True)
        self.assertIn(b'Login Unsuccessful. Please check email and password', response.data)

    # Ensure logout behaves correctly
    def test_correct_logout(self):
        with self.client:
            self.client.post('/login',
                            data=dict(email="ad@min.com", password="haslo"),
                            follow_redirects=True
            )
            response = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'You are successfully logged out', response.data)