# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import Config



app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PROT)

# 集成CSRF保护
csrf = CSRFProtect(app)
# 集成session
Session(app)