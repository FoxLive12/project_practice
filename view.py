from flask import render_template, request, redirect, url_for, flash
from app import app, Users, db, login_manager, create_project, allowed_file, classification
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import os
from werkzeug.utils import secure_filename

list_project = []

@app.route('/')
def index():
	list_project = os.listdir('project/'+current_user.user_name)
	return render_template("base.html", list=list_project)

@app.route('/login/register', methods=["POST", "GET"])
def register():
	if request.method == "POST":
		try:
			u = Users(user_name=request.form['user_name'],email=request.form['email'])
			u.set_password(request.form['psw'])
			db.session.add(u)
			db.session.flush()

			db.session.commit()

			os.mkdir('project/'+str(request.form['user_name']))
		except:
			db.session.rollback()
			print("Error")

	return render_template("register.html")

@app.route('/admin')
@login_required
def admin():
	list_project = os.listdir('project/'+current_user.user_name)
	return render_template('admin.html', list=list_project)

@app.route('/login', methods=['POST', "GET"])
def login():
	if request.method == "POST":
		user = db.session.query(Users).filter(Users.user_name == request.form['user_name']).first()
		if user and user.check_password(request.form['psw']):
			login_user(user)
			return redirect("/")
		else:
			flash("Invalid username/password", 'error')
			return redirect(url_for('login'))
	return render_template("login.html")

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))

@app.route('/create_project/', methods=['POST', "GET"])
@login_required
def project():
	if request.method == "POST":
		try:
			create_project(current_user.user_name, request.form['title_project'])
			return redirect(f"/create_project/{request.form['title_project']}/upload_files/")
		except FileExistsError:
			flash("Проект с таким именем уже существует", 'error')
		

	return render_template('create_project.html')

@app.route('/create_project/<name_project>/upload_files/', methods=['POST', "GET"])
@login_required
def upload_files(name_project):
	if request.method == "POST":
		if "file" not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files["file"]
		if file.filename == '':
			flash('Not selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print(filename)
			file.save(os.path.join('project/'+current_user.user_name+'/'+name_project, filename))
			return redirect(f'data_classification/{filename}')
		else:
			flash('Invalid file extension')

	return render_template('add_files.html')

@app.route('/create_project/<name_project>/upload_files/data_classification/<filename>')
def data_classification(name_project, filename):
	data_csv = classification(f"project/{current_user.user_name}/{name_project}/{filename}")
	return render_template("data_classification.html", data = data_csv)