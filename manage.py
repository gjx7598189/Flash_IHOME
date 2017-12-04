# -*- coding:utf-8 -*-
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from config import Config



app = Flask(__name__)


app.config.from_object(Config)

db = SQLAlchemy(app)

redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PROT)

# 集成CSRF保护
csrf = CSRFProtect(app)
# 集成session
Session(app)

manage = Manager(app)
# 集成数据库迁移
Migrate(app,db)
manage.add_command("db",MigrateCommand)

@app.route('/index',methods=["GET","POST"])
def index():
    session["name"] = "xiaohua"
    redis_store.set('name','xiaohei')
    return 'index'


if __name__ == '__main__':
    manage.run()