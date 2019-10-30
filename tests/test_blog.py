import pytest
# from models import *
# def test_index(client, auth):
#     response = client.get("/")
#     assert b"Login" in response.data
#
#     auth.login()
#     response = client.get("/")
#     assert b"Created on:" in response.data
#     assert b"likes" in response.data
#     assert b'href="/post/"' in response.data
#
# @pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
# def test_login_required(client, path):
#     response = client.post(path)
#     assert response.headers["Location"] == "http://localhost:5000/login"
#
# @pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
# def test_exists_required(client, auth, path):
#     auth.login()
#     assert client.post(path).status_code == 404
#
#
# def test_create(client, auth, app):
#     auth.login()
#     assert client.get("/post/0/edit/").status_code == 200
#     client.post("/post/0/update/", data={"title": "created", "body": "created test"})
#
#     with app.app_context():
#         count = Post.query.count()
#         assert count > 40
#
#
# def test_update(client, auth, app):
#     auth.login()
#     assert client.get("/post/1/edit/").status_code == 200
#     client.post("/post/1/update/", data={"title": "updated", "body": "updated test"})
#
#     with app.app_context():
#         post = Post.query.get(1)
#         assert post["title"] == "updated"
#
# def test_delete(client, auth, app):
#     auth.login()
#     response = client.get("/post/1/delete/")
#     assert response.headers["Location"] == "http://localhost:5000/post"
#
#     with app.app_context():
#         post = post = Post.query.get(1)
#         assert post is None