from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os




app = Flask(__name__)
SECRET_KEY = b"\x10\xfd\xb2\xca:\xe7\x1d\xdd\x19\xf7\xf2h\xf4\x99>\xaf\xf5Y\xfc\x18'\x91z\xc2\xd9~$n\x94\xf3\x9a\xb9"
#engine = create_engine('postgres://rulsyzlidrkofp:4492814d38bcfc278e6f25bfcc7fe43f15671737cb0d6477db5ccef9d5ad57b1@ec2-54-163-226-238.compute-1.amazonaws.com:5432/dblp20cuc3ltv1')
app.config['SECRET_KEY'] = SECRET_KEY
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://rulsyzlidrkofp:4492814d38bcfc278e6f25bfcc7fe43f15671737cb0d6477db5ccef9d5ad57b1@ec2-54-163-226-238.compute-1.amazonaws.com:5432/dblp20cuc3ltv1'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple' #simple
app.config['CACHE_DEFAULT_TIMEOUT'] = 30
#app.config['CACHE_MEMCACHED_SERVERS'] = 'mc3.dev.ec2.memcachier.com:11211'
#app.config['CACHE_MEMCACHED_USERNAME'] = '2E04B7'
#app.config['CACHE_MEMCACHED_PASSWORD'] = 'FC0338929429EFF54EB496647E8A660A'

cache = Cache(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from website import routes