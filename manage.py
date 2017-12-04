# -*- coding:utf-8 -*-
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

class Config(object):

    SECRET_KEY = "ToPd1bzuQBXhj+eTinSv7cNtbrBNiA2mfb+NhooZNQ6F5CfxlqF0zdG0Knahfvd/"

    DEBUG = True

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome17"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PROT = '6379'

    # Session 扩展配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PROT)
    PERMANENT_SESSION_LIFETIME = 86400

app = Flask(__name__)


app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PROT)

# 集成CSRF保护
csrf = CSRFProtect(app)
# 集成session
Session(app)


@app.route('/index',methods=["GET","POST"])
def index():
    session["name"] = "xiaohua"
    redis_store.set('name','xiaohei')
    return 'index'


if __name__ == '__main__':
    app.run()