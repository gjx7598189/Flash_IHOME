# -*- coding:utf-8 -*-
from flask import session

from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from ihome import app,db,redis_store

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