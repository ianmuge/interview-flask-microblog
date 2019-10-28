from app import db
from datetime import datetime
from flask_security import RoleMixin, UserMixin

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)
posts_users = db.Table(
    'posts_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer(), db.ForeignKey('post.id'))
)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='joined'))
    roles = db.relationship('Post', secondary=posts_users,backref=db.backref('users', lazy='joined'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    def __str__(self):
        return self.email
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def get_security_payload(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(255))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))