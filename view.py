from flask import render_template, request, redirect, url_for, flash
from app import app, Users, db, login_manager
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login/register', methods=["POST", "GET"])
def register():
	if request.method == "POST":
		try:
			u = Users(user_name=request.form['user_name'],email=request.form['email'])
			u.set_password(request.form['psw'])
			db.session.add(u)
			db.session.flush()

			db.session.commit()
		except:
			db.session.rollback()
			print("Error")

	return render_template("register.html")

@app.route('/admin')
@login_required
def admin():
	return render_template('admin.html')

@app.route('/login', methods=['POST', "GET"])
def login():
	if request.method == "POST":
		user = db.session.query(Users).filter(Users.user_name == request.form['user_name']).first()
		if user and user.check_password(request.form['psw']):
			login_user(user)
			return redirect(url_for('admin'))
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