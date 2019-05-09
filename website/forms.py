from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from website.models import User, PortfolioShell, StockShell
from website import db
from website.financial.stock import Stock
from website.financial import utility

class RegisterForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	security_question = StringField('Security Question', validators = [DataRequired()])
	security_answer = StringField('Answer')
	remember = BooleanField('Remember Me')
	submit = SubmitField("Sign Up")

	def validate_username(self, username):
		user =  User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("Sorry. That username is already taken. Please try another")

	def validate_password(self, password):
		if len(password.data) < 3:
			raise ValidationError("Error. Password must contain at least 15 characters, 4 special characters, letters of both cases, 3.5 characters in devnagiri script and a haiku.")

class LoginForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField("Log In!")	


class UsernameForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired()])
	submit = SubmitField("Request Question Authorization")

	def validate_username(self, username):
		user = User.query.filter_by(username = username.data).first()
		if not user:
			raise ValidationError("Sorry. You don't seem to have an account.")

class RedeemAccountForm(FlaskForm):
	# user = session['user']
	answer = StringField("Pointless Label")
	submit = SubmitField('Submit') 

class ResetPasswordForm(FlaskForm):
	password = PasswordField('New Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField("Sign Up")

class CreatePortfolioForm(FlaskForm):
	name = StringField('Name', validators = [DataRequired()])
	capital = FloatField("Capital", validators = [DataRequired()])
	submit = SubmitField("Create")

	def validate_capital(self, capital):
		if capital.data < 0:
			raise ValidationError("Error. Cannot have a negative starting capital")	

	def validate_name(self, name):
		portfolio =  PortfolioShell.query.filter_by(name=name.data).first()
		if portfolio:
			raise ValidationError("Sorry. That name is already taken. Please try another")

class AddStockForm(FlaskForm):
	name = StringField('Name', validators = [DataRequired()])
	ticker = StringField('Ticker', validators = [DataRequired()])
	exchange = SelectField('Exchange', choices = [("BSE","Bombay Stock Exchange"), ("NASDAQ","National Association of Securities Dealers Automated Quotations")], validators = [DataRequired()])
	n_shares = IntegerField("Number of Stocks", validators = [DataRequired()])
	submit = SubmitField("Add")	

	def validate_n_shares(self, n_shares):
		if n_shares.data < 0:
			raise ValidationError("Error. Cannot have a negative quantity of stocks")

	def validate_ticker(self, ticker):
		try:
			trial = Stock(self.name.data, self.ticker.data, self.exchange.data)
		except utility.NotFoundError:
			raise ValidationError("Error. The Ticker You Entered Is Not From That Exchange. Data Not Found Error.")
		except utility.OtherImportError:
			raise ValidationError("Some Import Error Occured")

class AnalysisForm(FlaskForm):
	pass
