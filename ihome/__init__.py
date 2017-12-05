# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import DevelopementConfig



app = Flask(__name__)

app.config.from_object(DevelopementConfig)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=DevelopementConfig.REDIS_HOST,port=DevelopementConfig.REDIS_PROT)

# 集成CSRF保护
csrf = CSRFProtect(app)
# 集成session
Session(app)