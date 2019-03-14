from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from website.models import User, PortfolioShell, StockShell
from website import db

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