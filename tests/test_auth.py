import os
import unittest
from app import app, db
from db import seed
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore,current_user
TEST_DB = './test.db'

class AuthTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ TEST_DB
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        seed()
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        db.session.flush()
        db.drop_all()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def login(self, email, password):
        return self.app.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.app.get(
            '/logout',
            follow_redirects=True
        )
    def login_as(self,role):
        if role=="admin":
            return self.login(email="admin@example.com",password="admin@2019")
        elif role=="publisher":
            return self.login(email="publisher@example.com",password="publisher@2019")
        else:
            return self.login(email="user@example.com", password="user@2019")

    def test_login_page(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Login' in response.data
    def test_authenticate(self):
        response = self.login_as("publisher")
        assert b'publisher' in response.data
    def test_invalid_user(self):
        response = self.login(email="bogus@bogus.com",password="bogus@2019")
        assert b'Specified user does not exist' in response.data

    def test_bad_password(self):
        response = self.login(email="publisher@example.com",password="publisher@example.com")
        assert b'Invalid password' in response.data

    def test_logout(self):
        self.login_as("publisher")
        response = self.logout()
        assert b'News Posts' in response.data

    def test_authorized_access(self):
        self.login_as("admin")
        response =self.app.get("/dashboard")
        assert b'dashboard' in response.data
    def test_unauthorized_access(self):
        self.login_as("publisher")
        response =self.app.get("/dashboard",follow_redirects=True)
        assert b"You do not have permission to view this resource." in response.data

if __name__ == "__main__":
    unittest.main()

# import base64
#
# from utils import authenticate, logout
#
# try:
#     from cookielib import Cookie
# except ImportError:
#     from http.cookiejar import Cookie
#
#
# def test_login_view(client):
#     response = client.get('/login')
#     assert b'Login' in response.data
#
#
# def test_authenticate(client):
#     response = authenticate(client)
#     assert response.status_code == 302
#     response = authenticate(client, follow_redirects=True)
#     assert b'Hello matt' in response.data
#
# def test_authenticate_case_insensitive_email(app, client):
#     response = authenticate(client, 'MATT@lp.com', follow_redirects=True)
#     assert b'Hello matt@lp.com' in response.data
# def test_login_form(client):
#     response = client.post('/login', data={'email': 'matt@lp.com'})
#     assert b'matt@lp.com' in response.data
#
# def test_unprovided_username(client, get_message):
#     response = authenticate(client, "")
#     assert get_message('EMAIL_NOT_PROVIDED') in response.data
#
#
# def test_unprovided_password(client, get_message):
#     response = authenticate(client, password="")
#     assert get_message('PASSWORD_NOT_PROVIDED') in response.data
#
#
# def test_invalid_user(client, get_message):
#     response = authenticate(client, email="bogus@bogus.com")
#     assert get_message('USER_DOES_NOT_EXIST') in response.data
#
#
# def test_bad_password(client, get_message):
#     response = authenticate(client, password="bogus")
#     assert get_message('INVALID_PASSWORD') in response.data
# def test_logout(client):
#     authenticate(client)
#     response = logout(client, follow_redirects=True)
#     assert b'Home Page' in response.data
#
#
# def test_logout_with_next(client, get_message):
#     authenticate(client)
#     response = client.get('/logout?next=http://google.com')
#     assert 'google.com' not in response.location
# def test_authorized_access(client):
#     authenticate(client)
#     response = client.get("/dashboard")
#     assert b'dashboard' in response.data
# def test_unauthorized_access(client, get_message):
#     authenticate(client, "joe@lp.com")
#     response = client.get("/dashboard", follow_redirects=True)
#     assert get_message('UNAUTHORIZED') in response.data
