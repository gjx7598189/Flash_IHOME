# -*- coding:utf-8 -*-

from . import api
from flask import request, abort, current_app, jsonify, make_response, json,session
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store,db
from ihome import constants
from ihome.models import User
from ihome.utils.response_code import RET


@api.route("/users", methods=["POST"])
def registe():

    # 获取参数判断是否空
    date_dict = request.json
    moblie = date_dict.get("moblie")
    phonecode = date_dict.get("phonecode")
    password = date_dict.get("password")

    if not all([moblie,phonecode,password]):
        return jsonify(erron=RET.PARAMERR,errmsg="参数不全")

    #取到本地验证码
    try:
        sms_code = redis_store.get("SMS_"+moblie)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DATAERR,errmsg="本地短信验证码获取失败")
    if not sms_code:
        return jsonify(erron=RET.NODATA,errmsg="短信验证码过期")
    # 本地验证码和传入的短信验证码进行对比
    if phonecode != sms_code:
        return jsonify(erron=RET.DATAERR,errmsg="短信验证码错误")

    user = User()
    user.name = moblie
    user.mobile = moblie
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="保存数据失败")

    # 保存登陆状态
    session["name"] = moblie
    session["moblie"] = moblie
    session["user_id"] = user.id

    return jsonify(erron=RET.OK,errmsg="注册成功")



