# -*- coding:utf-8 -*-
from . import api
from flask import session
from ihome import redis_store
from flask import current_app
import logging

@api.route('/index',methods=["GET","POST"])
def index():
    session["name"] = "xiaohua"
    redis_store.set('name','xiaohei')
    logging.debug("DEBUG LOGLOG")
    print ("===========================")
    current_app.logger.debug("DEBUG LOGLOGLOG CURRENT")
    return 'index'