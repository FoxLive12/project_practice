from flask import Flask, render_template
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import LoginManager, UserMixin

app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	user_name = db.Column(db.String(500), nullable=True)
	email = db.Column(db.String(500), unique=True)
	psw_hash = db.Column(db.String(500), nullable=True)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return f"<users {self.id}>"

	def set_password(self, password):
		self.psw_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.psw_hash, password)