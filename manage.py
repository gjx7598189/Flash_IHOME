# -*- coding:utf-8 -*-


from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from ihome import creat_name,db



# 通过传入不同的参数返回不同的app
app = creat_name("developement")
manage = Manager(app)
# 集成数据库迁移
Migrate(app,db)
manage.add_command("db",MigrateCommand)





if __name__ == '__main__':
    manage.run()