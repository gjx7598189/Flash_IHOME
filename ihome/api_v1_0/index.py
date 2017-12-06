# -*- coding:utf-8 -*-
from . import api
from flask import session
from ihome import redis_store


@api.route('/index',methods=["GET","POST"])
def index():
    session["name"] = "xiaohua"
    redis_store.set('name','xiaohei')
    return 'index'