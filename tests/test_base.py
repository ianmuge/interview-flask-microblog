import os
import unittest
from app import app, db,init_db_command
from db import seed
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore,current_user
TEST_DB = './test.db'

class BasicTests(unittest.TestCase):
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

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()