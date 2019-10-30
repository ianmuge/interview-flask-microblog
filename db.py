from app import *
import random
from faker import Faker
fake = Faker()
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
            title=fake.text(max_nb_chars=20),
            body= "".join(fake.paragraphs(5)),
            author_id=2,
            published=random.choice([True,False]),
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()
def reset():
    db.session.flush()
    if os.path.exists(cfg.db_file):
        os.remove(cfg.db_file)
        print("Database Removed")
    db.create_all()
    seed()
    echo("Initialized the database.")