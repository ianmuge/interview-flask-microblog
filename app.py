from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import login_required, roles_accepted
import cfg

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =cfg.mysql_db_resource

db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/')
def browse():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()
