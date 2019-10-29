from app import *
import random
import string
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
def seed():
    roles=["user","publisher","admin"]
    for r in roles:
        user_datastore.create_role(name=r)
    users=[
        {
            "username":"test-user",
            "email":'user@example.com',
            "password":'user@2019',
            "active":1,
            "roles":['user']
        },
        {
            "username": "test-publisher",
            "email": 'publisher@example.com',
            "password": 'publisher@2019',
            "active": 1,
            "roles": ['publisher']
        },
        {
            "username": "test-admin",
            "email": 'admin@example.com',
            "password": 'admin@2019',
            "active": 1,
            "roles": ['admin']
        }
    ]
    for u in users:
        user_datastore.create_user(username=u["username"],email=u['email'], password=u['password'],active=u["active"], roles=u['roles'])
    for p in range(40):
        post = Post(
            title=randomString(10),
            body=randomString(1000),
            author_id=2,
            published=random.choice([True,False]))
        db.session.add(post)
    db.session.commit()