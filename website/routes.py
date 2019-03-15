from flask import render_template, flash, url_for, redirect, request
from website.forms import RegisterForm, LoginForm, RedeemAccountForm, UsernameForm
from website.models import User, PortfolioShell, StockShell
from website import app, bcrypt, db, session
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
	
	return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegisterForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
		user = User(username = form.username.data, password = hashed_password, security_question = form.security_question.data, security_answer = form.security_answer.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Account Created for {form.username.data}. You can now log in!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', form= form, title = "Register")


@app.route("/login", methods= ['POST', 'GET'] )
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash(f'Welcome Back {user.username}')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccessful. Please check username and password', 'danger')
	return render_template('login.html', form = form, title = "Register")


@app.route("/logout")
def logout():
    logout_user()
    flash('Succesfully Logged Out', 'success')
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@app.route("/forgot_password", methods= ['POST', 'GET'] )
def forgot_password():

	form = UsernameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		session['redeem_data']= (user.security_question, user.security_answer)
		return redirect(url_for('redeem_account'))
	return render_template('forgot_password.html', form = form)

@app.route("/redeem_account", methods= ['POST', 'GET'] )
def redeem_account():
	form = RedeemAccountForm()
	if form.validate_on_submit():
		if form.answer.data == session.get('redeem_data', ("Impossible To Accidentally Guess String", ""))[1]:
			flash('Succesfully Done', 'success')
			session.pop('redeem_data', None)
			return redirect(url_for('login'))
		else:
			flash("Incorrect Answer. Try again", 'danger')
	return render_template('redeem_account.html', form = form, question = session.get('redeem_data', ("No Question To Ask You, Hacker!", ""))[0]  )

