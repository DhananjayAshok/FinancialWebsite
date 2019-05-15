from flask import render_template, flash, url_for, redirect, request
from website.forms import RegisterForm, LoginForm, RedeemAccountForm, UsernameForm, ResetPasswordForm, CreatePortfolioForm, AddStockForm
from website.models import User, PortfolioShell, StockShell
from website import app, bcrypt, db, session, cache
from flask_login import login_user, current_user, logout_user, login_required
from website.financial.portfolio import Portfolio
from website.financial.stock import Stock
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt
import mpld3

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
			flash(f'Welcome Back {user.username}', "success")
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

@app.route("/edit_portfolio/<int:portfolio_id>")
@login_required
def edit_portfolio(portfolio_id):
	command = request.args.get('command')
	portfolio = PortfolioShell.query.get_or_404(portfolio_id)
	if current_user != portfolio.holder:
		flash("That Portfolio Does Not Belong To You. You Can Not Make Edits To It.", "danger")
		return redirect(url_for('profile'))
	if command == "delete":
		stocks = StockShell.query.filter_by(portfolio=portfolio)
		for stock in stocks:
			db.session.delete(stock)
		db.session.delete(portfolio)
		db.session.commit()
		flash(f"Deleted Portfolio {portfolio.name}", "success")
	elif command == "change_capital":
		new_capital = request.args.get('capital')
		try:
			new_capital = int(new_capital)
		except:
			flash('Illegal URL Entry', "danger")
		else:
			if new_capital < 0:
				flash('You cannot have a negative capital', "danger")
			else:
				portfolio.capital=new_capital
				db.session.commit()
				flash(f"Changed Capital for {portfolio.name} to {portfolio.capital}", "success")
	else:
		flash('Illegal URL Entry', "danger")
	return redirect(url_for('profile'))

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



@app.route("/portfolio/create", methods = ['POST', 'GET'])
@login_required
def create_portfolio():
	form = CreatePortfolioForm()
	if form.validate_on_submit():
		portfolio = PortfolioShell(name = form.name.data, capital = form.capital.data, holder = current_user)
		db.session.add(portfolio)
		db.session.commit()
		flash(f'Succesfully created portfolio "{form.name.data}".', 'success')
		return redirect(url_for('profile'))
	return render_template('create_portfolio.html', title = "Create Portfolio", form = form)


def create_portfolio_optimized(portfolio_shell)->Portfolio:
	stock_shells = StockShell.query.filter_by(portfolio = portfolio_shell)
	# Creating the portfolio object
	stock_list = []
	for stock in stock_shells:
		"""
		Check if stock is already saved as a csv. If yes then make exchange internal otherwise download.
		"""
		data = (0,)
		# internal_path_string = "website/" + url_for('static', filename= f"{stock.name}({stock.ticker}).csv") 
		# path = Path(internal_path_string)
		# if path.is_file():
		if cache.get(f"{stock.name}({stock.ticker})") is not None:
			data = (stock.name, stock.ticker, "INTERNAL", stock.n_shares)
			flash(f"Stock {stock.name} has been found in the internal directories and has been loaded faster", "success")
		else:
			flash(f"Stock {stock.name} was loaded from online rather than internal directories", "danger")
			data = (stock.name, stock.ticker, stock.exchange, stock.n_shares)
		stock_list.append(data)

	return Portfolio(stock_list, portfolio_shell.capital)





@app.route('/portfolio/<int:portfolio_id>')
@login_required
def portfolio(portfolio_id):
	portfolio_shell = PortfolioShell.query.get_or_404(portfolio_id)
	stock_shells = StockShell.query.filter_by(portfolio = portfolio_shell)
	# Creating the portfolio object
	portfolio = create_portfolio_optimized(portfolio_shell)

	return render_template('portfolio.html', title = portfolio_shell.name, portfolio = portfolio, portfolio_shell = portfolio_shell, stock_shells = stock_shells, max_date=str(date.today()))



@app.route("/stock/add/<int:portfolio_id>", methods = ['POST', 'GET'])
@login_required
def add_stock(portfolio_id):
	portfolio_shell = PortfolioShell.query.get_or_404(portfolio_id)
	if current_user != portfolio_shell.holder:
		flash("That Portfolio Does Not Belong To You. You Can Not Make Edits To It.", "danger")
		return redirect(url_for('portfolio', portfolio_id=portfolio_id))
	form = AddStockForm()
	if form.validate_on_submit():
		portfolio = create_portfolio_optimized(portfolio_shell)
		stock_data = (form.name.data, form.ticker.data, form.exchange.data, form.n_shares.data)
		portfolio.buy_stock(stock_data, free= (not form.free.data))
		if portfolio.stocks.get(form.name.data, None) is None:
			flash(f"Not Enough Money To Make This Purchase!. You have only {portfolio.capital}", "danger")
		else:
			portfolio_shell.capital = portfolio.capital
			stock = StockShell(name = form.name.data, ticker = form.ticker.data, exchange = form.exchange.data, n_shares = portfolio.stocks.get(form.name.data)[1], portfolio = portfolio_shell)
			db.session.add(stock)
			db.session.commit()
			flash(f'Succesfully added Stock "{form.name.data}".', 'success')
			return redirect(url_for('portfolio', portfolio_id = portfolio_shell.id))
	return render_template('add_stock.html', title = "Add Stock", form = form)

@app.route("/stock/change/<int:portfolio_id>")
@login_required
def stock_change(portfolio_id):
	if current_user != PortfolioShell.query.get_or_404(portfolio_id).holder:
		flash("That Portfolio Does Not Belong To You. You Can Not Make Edits To It.", "danger")
		return redirect(url_for('portfolio', portfolio_id=portfolio_id))
	args = {}
	portfolio_shell = PortfolioShell.query.get_or_404(portfolio_id)
	try:
		command = request.args.get('command')
	except:
		args['command'] = "Invalid Command"
	free = request.args.get('free') 
	if free == "True":
		free = True
	elif free == "False":
		free = False
	else:
		args['free']= "Variable Free Was Not a Boolean."	
		
	try:
		n = int(request.args.get('n'))
	except:
		args['n']= "Variable number was not an integer"
	try: 
		stock_id = int(request.args.get('stock_id'))
	except:
		args['stock_id']="Stock ID did not exist"

	if len(args.keys()) != 0:
		flash(f"Something was wrong with the input. Check Error Dictionary:\n {args}", "danger")
		return redirect(url_for('portfolio',portfolio_id=portfolio_shell.id))


	portfolio = create_portfolio_optimized(portfolio_shell)


	if command == "buy":
		pass_in = (stock.name, stock.ticker, stock.exchange, n)
		portfolio.buy_stock(pass_in, free)

	else:
		portfolio.sell_stock(stock.name, n, free)

	if portfolio.stocks.get(stock.name, None) is None:
		db.session.delete(stock)
	else:	
		stock.n_shares = portfolio.stocks[stock.name][1]
	portfolio_shell.capital = portfolio.capital
	db.session.commit()
	flash(f'Transaction Completed Succesfully', 'success')
	return redirect(url_for('portfolio',portfolio_id=portfolio_shell.id))


@app.route("/analysis/<int:portfolio_id>")
def analysis(portfolio_id):
	portfolio_shell = PortfolioShell.query.get_or_404(portfolio_id)
	command = request.args.get('command')
	stock_list = []
	stock_shells = StockShell.query.filter_by(portfolio= portfolio_shell)
	for stock in stock_shells:
		data = (stock.name, stock.ticker, 'INTERNAL', stock.n_shares)
		stock_list.append(data)
	portfolio = Portfolio(stock_list, portfolio_shell.capital)

	if command == 'computeActions':
		method = request.args.get('method')
		final = portfolio.computeActions(method= method)
		#figs = portfolio.create_Graph(method=method)
		#for name in figs:
		#	mpld3.show(figs[name])
		return render_template('computeActions.html', method= method, actions=final, portfolio_id=portfolio_id)
	elif command == 'simulateAnalysis':
		method = request.args.get('method')
		start_date = request.args.get('start_date')
		temp = start_date.split('-')
		start_date = tuple([int(value) for value in temp])
		frequency = request.args.get('frequency')
		if not frequency:
			frequency = 7
		else:
			frequency = int(frequency)
		final = portfolio.simulateAnalysis(method=method, start_date=start_date, frequency=frequency)
		return render_template('simulateAnalysis.html', method= method, actions=final)
	elif command == 'displayGraph':
		pass
	flash("Invalid Command. (Wait for page to load before selecting)", "danger")
	return render_template('computeActions.html', method= "Invalid Method", actions={})


@app.route("/graph/<int:portfolio_id>", methods=['GET'])
def graph(portfolio_id):
	portfolio_shell = PortfolioShell.query.get_or_404(portfolio_id)
	stock_shells = StockShell.query.filter_by(portfolio=portfolio_shell)
	name = request.args.get('name')
	method = request.args.get('method')
	stock = stock_shells[0]
	for candidate in stock_shells:
		if candidate.name == name:
			stock = candidate
			break
	a = Stock(stock.name, stock.ticker, "INTERNAL")
	fig = a.create_Graph(method, a.implimentAnalysis(method))
	data = mpld3.fig_to_html(fig)
	plt.close()
	return data





@app.route("/trials/<int:portfolio_id>")
@login_required
def trials(portfolio_id):
	context = {}
	if portfolio_id == 1:
		flash("We cached portfolio_id 1")
		cache.set('id', portfolio_id)
	else:
		flash(f"cache value is {cache.get('id')}")

	return render_template('trials.html', portfolio_id=portfolio_id, context = context)