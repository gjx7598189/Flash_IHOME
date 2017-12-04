# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):

    DEBUG = True
    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome17"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)


app.config.from_object(Config)

db = SQLAlchemy(app)


@app.route('/index')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()