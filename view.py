from flask import render_template, request, redirect, url_for, flash, send_file, safe_join
from app import app, Users, db, login_manager, create_project, allowed_file, classification, Projects, csv_writer
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
import os
from werkzeug.utils import secure_filename

list_project = []

@app.route('/', methods=['POST', 'GET'])
@login_required
def index():
	list_project = os.listdir('project/'+current_user.user_name)
	if request.method == "POST":
		query = Projects.query.filter_by(title_project=request.form['title_card'], project_username=current_user.user_name).all()
		return redirect(f"/create_project/{current_user.user_name}/{query[0].title_project}/upload_files/add_classes/data_classification/{query[0].file_name}")

	return render_template("base.html", list=list_project)

@app.route('/login/register', methods=["POST", "GET"])
def register():
	if request.method == "POST":
		try:
			search_username = Users.query.filter_by(user_name = request.form['user_name']).all()
			search_email = Users.query.filter_by(email = request.form['email']).all()
			if request.form['user_name'] != "" and request.form['email'] != "" and request.form['psw'] != "":
				if search_username == []:
					if search_email == []:
						u = Users(user_name=request.form['user_name'],email=request.form['email'])
						u.set_password(request.form['psw'])
						db.session.add(u)
						db.session.flush()
						db.session.commit()
						os.mkdir('project/'+str(request.form['user_name']))
						return redirect(url_for('login'))
					else:
						flash("Email is already in use")
				else:
					flash("Username is already in use")
			else:
				flash("Fill in all the fields")

		except:
			db.session.rollback()
			print("Error")

	return render_template("register.html")

@app.route('/login', methods=['POST', "GET"])
def login():
	if request.method == "POST":
		user = db.session.query(Users).filter(Users.user_name == request.form['user_name']).first()
		if user and user.check_password(request.form['psw']):
			rm = True if request.form.get('cb_remember') else False
			login_user(user, remember=rm)
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
			return redirect(f"/create_project/{current_user.user_name}/{request.form['title_project']}/upload_files/")
		except FileExistsError:
			flash("Проект с таким именем уже существует", 'error')

	return render_template('create_project.html', name=current_user.user_name)

@app.route('/create_project/<name_user>/<name_project>/upload_files/', methods=['POST', "GET"])
@login_required
def upload_files(name_user, name_project):
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
			file.save(os.path.join('project/'+current_user.user_name+'/'+name_project, filename))
			return redirect(f'add_classes/{filename}')
		else:
			flash('Invalid file extension')

	return render_template('add_files.html')

@app.route('/create_project/<name_user>/<name_project>/upload_files/add_classes/<filename>', methods=['POST', "GET"])
@login_required
def add_classes(name_user, name_project, filename):
	u = Users.query.filter_by(id = 1).all()
	p = Projects(title_project=name_project, file_name=filename, project_username=current_user.user_name, u_id=u[0].id, class_list="")
	search_project = Projects.query.filter_by(title_project=name_project, project_username=current_user.user_name).all()
	if search_project != []:
		if request.method == "POST":
			if '+' in request.form:
				if request.form['title_class'] == "":
					flash("Название класса не может быть пустым")
				else:
					query = Projects.query.filter_by(title_project=name_project, project_username=current_user.user_name).all()
					list_=query[0].class_list.split()
					list_.append(request.form['title_class'])
					l = " ".join(list_)
					Projects.query.filter_by(title_project=name_project, project_username=current_user.user_name).update({"class_list": l})
					db.session.commit()
			if 'continue' in request.form:
				return redirect(f"data_classification/{filename}")
	else:
		db.session.add(p)
		db.session.commit()

	query = Projects.query.filter_by(title_project=name_project, project_username=current_user.user_name).all()
	local_list = query[0].class_list.split()
	return render_template('add_classes.html', classes=local_list)

@app.route('/create_project/<name_user>/<name_project>/upload_files/add_classes/data_classification/<filename>', methods=['POST', "GET"])
@login_required
def data_classification(name_user, name_project, filename):
	path = f"project/{current_user.user_name}/{name_project}/{filename}"
	sorted_path="sorted.txt"
	data_csv, column_names = classification(path)
	data_csv_changed = []
	for item in data_csv:
		r = " ".join(item)
		data_csv_changed.append(r)
	query = Projects.query.filter_by(title_project=name_project, project_username=current_user.user_name).all()
	local_list = query[0].class_list.split()

	if request.method == "POST":
		dict = {}
		k = []
		sorted_list = []
		for item in data_csv_changed:
			d1 = {str(item): str(request.form.get(item))}
			dict.update(d1)
		for i in sorted(dict.items(), key=lambda para: para[1]):
			k.append(data_csv_changed.index(i[0]))
		for i in k:
			sorted_list.append(data_csv[i])
		csv_writer(sorted_list, current_user.user_name, name_project, column_names)
		download_path=f"project/{name_user}/{name_project}/sorted.csv"
		try:
			return send_file(download_path, as_attachment=True)
		except Exception as e:
			return str(e)

	return render_template("data_classification.html", data = data_csv_changed, classes=local_list, paht=sorted_path)