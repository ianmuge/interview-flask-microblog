from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore,current_user
from flask.cli import with_appcontext
from click import command, echo
from datetime import datetime
from flask_paginate import Pagination, get_page_parameter
import cfg

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =cfg.mysql_db_resource
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SECRET_KEY'] = cfg.secret_key
app.config['SECURITY_PASSWORD_SALT'] = cfg.security["SALT"]


db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from db import seed

@command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.session.flush()
    if os.path.exists(cfg.db_file):
        os.remove(cfg.db_file)
        print("Database Removed")
    db.create_all()
    seed()
    echo("Initialized the database.")
app.cli.add_command(init_db_command)

from sqlalchemy import func
@app.route('/')
def index():
    sort_by=request.args.get("sort_by", type=int, default=1)
    posts = Post.query.filter_by(published=True)
    if sort_by==1:
        posts=posts.order_by(Post.timestamp.asc())
    elif sort_by==2:
        posts=posts.order_by(Post.timestamp.desc())
    elif sort_by==3:
        posts = posts.order_by(Post.popularity.desc())
    else:
        posts=posts.order_by(Post.timestamp.desc())
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=posts.count(), record_name='posts',css_framework='foundation',per_page_parameter='sort_by')
    return render_template('index.html',posts=posts,pagination=pagination)
@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/dashboard/')
@roles_accepted("admin")
@login_required
def dashboard():
    return render_template('post/dashboard.html')

@app.route('/post/', methods=['GET'])
@roles_accepted("publisher")
@login_required
def get_user_posts():
    posts=Post.query.filter_by(author_id = session["user_id"])
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=posts.count(), record_name='posts',css_framework='foundation')
    return render_template('post/index.html', posts=posts.all(),pagination=pagination)

@app.route('/post/<int:id>', methods=['GET'])
@roles_accepted("publisher")
@login_required
def get_post(id):
    post=Post.query.filter_by(id = id).first()
    return render_template('detail.html', id=id,post=post)
@app.route('/post/<int:id>/edit/', methods=['GET'])
@roles_accepted("publisher")
@login_required
def edit_post(id):
    if id==0:
        post={}
    else:
        post=Post.query.filter_by(id = id).first()
    return render_template('post/edit.html', id=id,post=post)

@app.route('/post/<int:id>/update/', methods=['POST'])
@roles_accepted("publisher")
@login_required
def update_post(id):
    if request.form.get('title') and request.form.get('body'):
        if id!=0:
            post=Post.query.filter_by(id = id).first()
            post.title=request.form['title']
            post.body=request.form['body']
            post.author_id=session["user_id"]
            post.published=request.form.get('published')=="1" or False
            db.session.flush()
            db.session.commit()
        else:
            post = Post(
                title=request.form['title'],
                body=request.form['body'],
                author_id=session["user_id"],
                published=request.form.get('published')=="1" or False)
            db.session.add(post)
            db.session.commit()
        flash('Post added/updated successfully.', 'success')
        return redirect(url_for('get_user_posts'))
    else:
        flash('Required fields not supplied', 'danger')
        db.session.rollback()
        return redirect(url_for('get_user_posts'))
@app.route('/post/<int:id>/delete/', methods=['GET'])
@roles_accepted("publisher")
@login_required
def delete_post(id):
    try:
        post = db.session.query(Post).get(id)
        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted successfully.', 'success')
        return redirect(url_for('get_user_posts'))
    except Exception as exc:
        flash('Could not delete post! Exception: {0}'.format(exc), 'danger')
        db.session.rollback()
        return redirect(url_for('get_user_posts'))
@app.route('/post/<int:id>/like/', methods=['POST'])
@roles_accepted("user","publisher")
@login_required
def like_post(id):
    try:
        post = Post.query.filter_by(id=id).first_or_404()
        if current_user.has_liked_post(post):
            current_user.unlike_post(post)
            post.popularity-=1
            db.session.flush()
            db.session.commit()
            next="Like"
        else:
            current_user.like_post(post)
            post.popularity += 1
            db.session.flush()
            db.session.commit()
            next="Unlike"
        data = {
            "count": post.likes.count(),
            "next": next
        }
        return data
    except Exception as exc:
        flash('Exception: {0}'.format(exc), 'danger')
        return redirect(url_for('get_user_posts'))
if __name__ == '__main__':
    app.run()
