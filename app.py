import os
from flask import Flask
from models.models import db, create_admin

current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir,"models","database.sqlite3")
db.init_app(app)

with app.app_context():
    db.create_all()
    create_admin()

from controllers.main import *

if __name__ ==  '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)