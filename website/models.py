from website import db, login_manager
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    security_question = db.Column(db.String, nullable = False)
    security_answer = db.Column(db.String, nullable = False)
    portfolios = db.relationship('PortfolioShell', backref='holder', lazy=True)

    def __repr__(self):
        return f"User('{self.username}')"

class PortfolioShell(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True, nullable = False)
	capital = db.Column(db.Float, default = 1.0)
	stocks = db.relationship('StockShell', backref='portfolio', lazy=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)


	def __repr__(self):
		return f"Portfolio'({self.name})'"

class StockShell(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=False, nullable=False)
	ticker = db.Column(db.String, unique=False, nullable=False)
	exchange = db.Column(db.String, nullable=False)
	n_shares = db.Column(db.Integer, nullable = False, default = 0)
	portfolio_id = db.Column(db.Integer, db.ForeignKey(PortfolioShell.id),nullable=False)

	def __repr__(self):
		return f"Stock('{self.name}')"