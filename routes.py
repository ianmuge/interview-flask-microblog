from flask import *
from flask_paginate import Pagination, get_page_parameter
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore,current_user
from app import db,app
from models import *
@app.route('/')
def index():
    sort_by=request.args.get("sort_by", type=int)
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
    return render_template('post/dashboard.html',users=User,posts=Post)

@app.route('/post/', methods=['GET'])
@roles_accepted("publisher","admin")
@login_required
def get_user_posts():
    posts=Post.query.filter_by(author_id = session["user_id"])
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=posts.count(), record_name='posts',css_framework='foundation')
    return render_template('post/index.html', posts=posts.all(),pagination=pagination)

@app.route('/post/<int:id>', methods=['GET'])
@roles_accepted("publisher","user","admin")
@login_required
def get_post(id):
    post=Post.query.filter_by(id = id).first()
    return render_template('detail.html', id=id,post=post)

@app.route('/post/<int:id>/edit/', methods=['GET'])
@roles_accepted("publisher","admin")
@login_required
def edit_post(id):
    if id==0:
        post={}
    else:
        post=Post.query.filter_by(id = id).first()
    return render_template('post/edit.html', id=id,post=post)

@app.route('/post/<int:id>/update/', methods=['POST'])
@roles_accepted("publisher","admin")
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
@roles_accepted("publisher","admin")
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
@roles_accepted("user","publisher","admin")
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
        app.logger.exception(exc)
    finally:
        return data
@app.route('/post/comment/<int:comment_id>', methods=['GET'])
@roles_accepted("user","publisher","admin")
@login_required
def get_comment(comment_id):
    res={}
    try:
        comment = PostComment.query.get(comment_id)
        res = PostCommentSchema().jsonify(comment)
    except Exception as exc:
        app.logger.exception(exc)
        res = {
            "data": "",
            "code": 0,
            "msg": "Exception Raised: {0}".format(exc)
        }
    finally:
        return res
@app.route('/post/comment/create/', methods=['POST'])
@roles_accepted("user","publisher","admin")
@login_required
def create_comment_post():
    post_id=request.form['post_id']
    try:
        comment = PostComment(
            user_id=current_user.id,
            post_id = post_id,
            comment = request.form['comment']
        )
        db.session.add(comment)
        db.session.commit()

        flash('Comment added successfully.', 'success')
        res = {
            "data": "",
            "code": 1,
            "msg": "Added Successfully"
        }
    except Exception as exc:
        app.logger.exception(exc)
        res = {
            "data": "",
            "code": 0,
            "msg": "Exception Raised: {0}".format(exc)
        }
    finally:
        return res
@app.route('/post/comment/<int:comment_id>/update/', methods=['PUT'])
@roles_accepted("user","publisher","admin")
@login_required
def update_comment_post(comment_id):
    try:
        comment = PostComment.query.get(comment_id)
        comment.comment = request.form['edit_comment']
        db.session.flush()
        db.session.commit()
        flash('Comment updated successfully.', 'success')
        res = {
            "data": "",
            "code": 1,
            "msg": "Updated Successfully"
        }
    except Exception as exc:
        app.logger.exception(exc)
        res = {
            "data": "",
            "code": 0,
            "msg": "Exception Raised: {0}".format(exc)
        }
    finally:
        return res

@app.route('/post/comment/<int:comment_id>/delete/', methods=['DELETE'])
@roles_accepted("user","publisher","admin")
@login_required
def delete_comment_post(comment_id):
    try:
        comment = db.session.query(PostComment).get(comment_id)
        db.session.delete(comment)
        db.session.commit()
        res = {
            "data": "",
            "code": 1,
            "msg": "Comment Deleted Successfully"
        }
        flash('Comment deleted.', 'success')
    except Exception as exc:
        app.logger.exception(exc)
        res = {
            "data": "",
            "code": 0,
            "msg": "Exception Raised: {0}".format(exc)
        }
    finally:
        return res