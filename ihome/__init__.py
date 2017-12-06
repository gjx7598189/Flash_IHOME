# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config


redis_store = None
db = SQLAlchemy()
csrf = CSRFProtect()


def creat_name(creat_name):
    '''工厂模式根据不同的参数制造不同的app'''

    app = Flask(__name__)

    app.config.from_object(config[creat_name])

    db.init_app(app)

    global redis_store
    redis_store = redis.StrictRedis(host=config[creat_name].REDIS_HOST,port=config[creat_name].REDIS_PROT)

    # 集成CSRF保护
    csrf.init_app(app)
    # 集成session
    Session(app)
    # 注册蓝图
    from ihome import api_v1_0
    app.register_blueprint(api_v1_0.api)

    return app