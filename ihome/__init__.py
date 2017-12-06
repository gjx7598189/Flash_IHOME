# -*- coding:utf-8 -*-

from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config


redis_store = None
db = SQLAlchemy()
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


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