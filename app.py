from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore
from flask.cli import with_appcontext
from click import command, echo
from datetime import datetime
import cfg

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
    likes = db.relationship('Post', secondary='posts_users',backref=db.backref('users', lazy='joined'))
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
    published= db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@command("init-db")
@with_appcontext
def init_db_command():
    """Initialize the database."""
    db.create_all()
    user_datastore.create_user(username="TestUser",email='user@example.com', password='password',active=1)
    db.session.commit()
    echo("Initialized the database.")
app.cli.add_command(init_db_command)

@app.route('/')
def index():
    posts = Post.query.filter_by(published=True).order_by(Post.timestamp.desc())
    return render_template('index.html',posts=posts)
@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/post/', methods=['GET'])
@login_required
def get_user_posts():
    posts=Post.query.filter_by(author_id = session["user_id"]).all()
    return render_template('post/index.html', posts=posts)

@app.route('/post/<int:id>', methods=['GET'])
@login_required
def get_post(id):
    post=Post.query.filter_by(id = id).first()
    return render_template('detail.html', id=id,post=post)
@app.route('/post/<int:id>/edit/', methods=['GET'])
@login_required
def edit_post(id):
    if id==0:
        post={}
    else:
        post=Post.query.filter_by(id = id).first()
    return render_template('post/edit.html', id=id,post=post)

# @app.route('/post/', methods=['POST'])
# def create_post():
#     if request.form.get('title') and request.form.get('body'):
#         post=Post(
#             title=request.form['title'],
#             body=request.form['body'],
#             author_id=1,
#             published=request.form.get('published') or False)
#         db.session.add(post)
#         db.session.commit()
#         flash('Post created successfully.', 'success')
#         return redirect(url_for('get_user_posts'))
#     else:
#         flash('Title and Content are required.', 'danger')
#         db.session.rollback()
#         return redirect(url_for('get_user_posts'))

@app.route('/post/<int:id>/update/', methods=['POST'])
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

@app.route('/post/<int:id>/like/', methods=['GET'])
def like_post(id):
    try:
        return redirect(url_for('get_user_posts'))
    except Exception as exc:
        flash('Exception: {0}'.format(exc), 'danger')
        return redirect(url_for('get_user_posts'))
if __name__ == '__main__':
    app.run()
