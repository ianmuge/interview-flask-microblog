import os
import unittest
from app import app, db
from db import seed
import pytest
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore,current_user
TEST_DB = './test.db'
from models import Post

class BlogTests(unittest.TestCase):
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

#     def tearDown(self):
#         db.session.flush()
#         db.drop_all()
#         if os.path.exists(TEST_DB):
#             os.remove(TEST_DB)

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
    def login_as(self,role="user"):
        if role=="admin":
            return self.login(email="admin@example.com",password="admin@2019")
        elif role=="publisher":
            return self.login(email="publisher@example.com",password="publisher@2019")
        else:
            return self.login(email="user@example.com", password="user@2019")

    def test_index(self):
        response = self.app.get("/")
        assert b"Login" in response.data
        self.login_as()
        response = self.app.get("/")
        assert b"Created on:" in response.data
        assert b"likes" in response.data

    def test_create(self):
        self.login_as("publisher")
        assert self.app.get("/post/0/edit/").status_code == 200
        self.app.post("/post/0/update/", data={"title": "created", "body": "created test"})
        count = Post.query.count()
        assert count > 40

    def test_not_exists(self):
        self.login_as("publisher")
        assert self.app.get("/post/102",follow_redirects=True).status_code == 404
    def test_exists(self):
        self.login_as("publisher")
        assert self.app.get("/post/2",follow_redirects=True).status_code == 200

    def test_update(self):
        self.login_as("publisher")
        assert self.app.get("/post/1/edit/").status_code == 200
        self.app.post("/post/1/update/", data={"title": "updated", "body": "updated test"})
        post = Post.query.get(1)
        assert post.title == "updated"

    def test_delete(self):
        self.login_as("publisher")
        response = self.app.get("/post/1/delete/",follow_redirects=True)
        assert b'Post Deleted successfully.' in response.data
        post = post = Post.query.get(1)
        assert post is None

if __name__ == "__main__":
    unittest.main()
