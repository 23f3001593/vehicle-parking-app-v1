import os
from flask import Flask
from flask_login import LoginManager
from models.models import db, User, create_admin
import secrets

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir,"models","database.sqlite3")
app.config['SECRET_KEY'] = secrets.token_hex(32)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    create_admin()

from resources.api import create_api
create_api(app)

from controllers.main import *
from controllers.admin import *
from controllers.user import *

if __name__ ==  '__main__':
    app.run(host='127.0.0.1', port=5000)