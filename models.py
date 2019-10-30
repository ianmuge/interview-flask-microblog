from app import db,ma
from datetime import datetime
from flask_security import RoleMixin, UserMixin
import cfg

class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))

class PostsUsers(db.Model):
    __tablename__ = 'posts_users'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    post_id = db.Column('post_id', db.Integer(), db.ForeignKey('post.id'))

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
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary='roles_users',backref=db.backref('users', lazy='joined'))
    liked = db.relationship('PostLike', foreign_keys='PostLike.user_id', backref='user', lazy='dynamic')
    commented = db.relationship('PostComment', foreign_keys='PostComment.user_id', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __str__(self):
        return self.email
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(user_id=self.id,post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(PostLike.user_id == self.id,PostLike.post_id == post.id).count() > 0

    def get_security_payload(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }

class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

class PostComment(db.Model):
    __tablename__ = 'post_comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)

class PostCommentSchema(ma.Schema):
    class Meta:
        fields = ('id','user_id', 'post_id','comment')
class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(255))
    body = db.Column(db.Text)
    published= db.Column(db.Boolean)
    popularity = db.Column(db.Integer,default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    comments = db.relationship('PostComment', backref='post', lazy='dynamic')
