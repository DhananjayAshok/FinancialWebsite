from flask import render_template, flash, url_for, redirect, request
from website.forms import RegisterForm, LoginForm, RedeemAccountForm, UsernameForm, ResetPasswordForm, CreatePortfolioForm, AddStockForm
from website.models import User, PortfolioShell, StockShell
from website import app, bcrypt, db, session
from flask_login import login_user, current_user, logout_user, login_required
from website.financial.portfolio import Portfolio

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
	#p = Portfolio([("Apple","AAPL","NASDAQ",5)])
	portfolios = PortfolioShell.query.filter_by(holder = current_user)
	return render_template('profile.html', title='Profile', portfolios = portfolios)

@app.route("/forgot_password", methods= ['POST', 'GET'] )
def forgot_password():
	form = UsernameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		session['redeem_data']= (user.security_question, user.security_answer, user.id)
		return redirect(url_for('redeem_account'))
	return render_template('forgot_password.html', title = "Forgot Password", form = form)

@app.route("/redeem_account", methods= ['POST', 'GET'] )
def redeem_account():
	form = RedeemAccountForm()
	if form.validate_on_submit():
		if form.answer.data == session.get('redeem_data', ("Impossible To Accidentally Guess String", ""))[1]:
			return redirect(url_for('reset_password'))
		else:
			flash("Incorrect Answer. Try again", 'danger')
	return render_template('redeem_account.html', form = form, title = "Redeem Account", question = session.get('redeem_data', ("No Question To Ask You, Hacker!", ""))[0]  )


@app.route("/reset_password", methods = ['POST', 'GET'])
def reset_password():
	if session.get('redeem_data', None) is None:
		flash('Verify Credentials First', 'danger')
		return redirect(url_for('forgot_password'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(id = session.get('redeem_data', [None, None, None])[2]).first()
		if not user:
			flash('An unknown error occured. Account is corrupted.', 'danger')
			return redirect('home')
		else:
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
			user.password = hashed_password
			db.session.commit()
			session.pop('redeem_data', None)
			flash(f'Succesfully changed password for {user.username}.', 'success')
			return redirect('login')
	return render_template('reset_password.html', title = "Reset Password", form = form)


@login_required
@app.route("/portfolio/create", methods = ['POST', 'GET'])
def create_portfolio():
	form = CreatePortfolioForm()
	if form.validate_on_submit():
		portfolio = PortfolioShell(name = form.name.data, capital = form.capital.data, holder = current_user)
		db.session.add(portfolio)
		db.session.commit()
		flash(f'Succesfully created portfolio "{form.name.data}".', 'success')
		return redirect(url_for('profile'))
	return render_template('create_portfolio.html', title = "Create Portfolio", form = form)


@login_required
@app.route('/portfolio/<int:portfolio_id>')
def portfolio(portfolio_id):
	portfolio = PortfolioShell.query.get_or_404(portfolio_id)
	stocks = StockShell.query.filter_by(portfolio = portfolio)
	return render_template('portfolio.html', title = portfolio.name, portfolio = portfolio, stocks = stocks)


@login_required
@app.route("/stock/add/<int:portfolio_id>", methods = ['POST', 'GET'])
def add_stock(portfolio_id):
	portfolio = PortfolioShell.query.get_or_404(portfolio_id)
	form = AddStockForm()
	if form.validate_on_submit():
		stock = StockShell(name = form.name.data, ticker = form.ticker.data, exchange = form.exchange.data, n_shares = form.n_shares.data, portfolio = portfolio)
		db.session.add(stock)
		db.session.commit()
		flash(f'Succesfully added Stock "{form.name.data}".', 'success')
		return redirect(url_for('portfolio', portfolio_id = portfolio.id))
	return render_template('add_stock.html', title = "Add Stock", form = form)