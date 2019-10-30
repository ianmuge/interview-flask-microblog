from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import login_required, roles_accepted,RoleMixin, UserMixin,Security, SQLAlchemyUserDatastore,current_user
from flask.cli import with_appcontext
from click import command, echo
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_marshmallow import Marshmallow
import cfg
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =cfg.mysql_db_resource
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
app.config['SECRET_KEY'] = cfg.secret_key
app.config['SECURITY_PASSWORD_SALT'] = cfg.security_salt
app.config['SECURITY_TRACKABLE'] = True

# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# admin = Admin(app, name='News', template_mode='bootstrap3')


db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)

from models import *
from routes import *
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


# class UserView(ModelView):
#     column_exclude_list = ['password', ]

# admin.add_view(UserView(User, db.session))
# admin.add_view(ModelView(Post, db.session))

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


if __name__ == '__main__':
    app.run()
