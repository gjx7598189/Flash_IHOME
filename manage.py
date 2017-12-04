# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect

class Config(object):

    SECRET_KEY = "ToPd1bzuQBXhj+eTinSv7cNtbrBNiA2mfb+NhooZNQ6F5CfxlqF0zdG0Knahfvd/"


    DEBUG = True
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome17"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    #redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PROT = '6379'

app = Flask(__name__)


app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PROT)
# 集成CSRF保护
csrf = CSRFProtect(app)

@app.route('/index',methods=["GET","POST"])
def index():
    redis_store.set('name','xiaohei')
    return 'index'


if __name__ == '__main__':
    app.run()