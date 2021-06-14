from flask import Flask, render_template, redirect, url_for
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import LoginManager, UserMixin
import os
import csv

ALLOWED_EXTENSIONS = set(['csv'])
app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)

def create_project(username, project_title):
	os.mkdir('project/'+username+'/'+project_title)

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	user_name = db.Column(db.String(500), nullable=True, unique=True)
	email = db.Column(db.String(500), unique=True)
	psw_hash = db.Column(db.String(500), nullable=True)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return f"<users {self.id}>"

	def set_password(self, password):
		self.psw_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.psw_hash, password)

class Projects(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	title_project = db.Column(db.String(500))
	file_name = db.Column(db.String(500))
	class_list = db.Column(db.String(500))
	project_username = db.Column(db.String(500))
	u_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def __repr__(self):
		return f"<projects {self.id}>"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def classification(path):
	with open(path, "r") as f_obj:
		reader = csv.reader(f_obj, delimiter=';')
		data_list = []
		count = 0
		for row in reader:
			if count == 0:
				count += 1
				column_names = row
				continue
			data_list.append(row)

		return data_list, column_names

def csv_writer(sort_row, user_name, name_project, column_names):
		try:
			f = open("project/"+user_name+"/"+name_project+"/sorted.csv", "x")
			f.close()
			with open("project/"+user_name+"/"+name_project+"/sorted.csv", mode="w", encoding='utf-8') as w_file:
				file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\r", dialect='excel')
				file_writer.writerow(column_names)
				for i in sort_row:
					file_writer.writerow(i)
		except FileExistsError as e:
			with open("project/"+user_name+"/"+name_project+"/sorted.csv", mode="w", encoding='utf-8') as w_file:
				file_writer = csv.writer(w_file, delimiter = ";", lineterminator="\r", dialect='excel')
				file_writer.writerow(column_names)
				for i in sort_row:
					file_writer.writerow(i)