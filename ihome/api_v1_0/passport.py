# -*- coding:utf-8 -*-

from . import api
from flask import request, current_app, jsonify, session
from ihome import redis_store,db
from ihome.models import User
from ihome.utils.response_code import RET

# 判断用户是否登陆
@api.route("/session")
def check_user_login():
    # 判断用户是否登陆，如果登陆返回用户的id，用户名
    user_id = session.get("user_id")
    name = session.get("name")
    return jsonify(erron=RET.OK,errmsg="OK",data={"user_id":user_id,"name":name})



# 用户登陆
@api.route("/session",methods=["POST"])
def login():
    # 获取参数
    data_dict = request.json
    mobile = data_dict.get("mobile")
    password = data_dict.get("password")
    if not all([mobile,password]):
        return jsonify(erron=RET.DATAERR,errmsg="数据不完整")
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DATAERR,errmsg="查询数据失败")
    if not user:
        return jsonify(erron=RET.USERERR,errmsg="用户不存在")
    if not user.check_password(password):
        return jsonify(erron=RET.PWDERR,errmsg="用户名或密码错误")

    # 保存登陆状态，并返回结果
    session["name"] = user.name
    session["moblie"] = user.mobile
    session["user_id"] = user.id
    return jsonify(erron=RET.OK,errmsg="登陆成功")


# 退出登陆
@api.route("/session",methods=["DELETE"])
def logout():
    # 清楚用户登陆信息
    session.pop("name",None)
    session.pop("mobile", None)
    session.pop("user_id", None)
    return jsonify(erron=RET.OK,errmsg="OK")




@api.route("/users", methods=["POST"])
def registe():

    # 获取参数判断是否空
    date_dict = request.json
    mobile = date_dict.get("mobile")
    phonecode = date_dict.get("phonecode")
    password = date_dict.get("password")

    if not all([mobile,phonecode,password]):
        return jsonify(erron=RET.PARAMERR,errmsg="参数不全")

    #取到本地验证码
    try:
        sms_code = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DATAERR,errmsg="本地短信验证码获取失败")
    if not sms_code:
        return jsonify(erron=RET.NODATA,errmsg="短信验证码过期")
    # 本地验证码和传入的短信验证码进行对比
    if phonecode != sms_code:
        return jsonify(erron=RET.DATAERR,errmsg="短信验证码错误")

    user = User()
    user.name = mobile
    user.mobile = mobile
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="保存数据失败")

    # 保存登陆状态
    session["name"] = mobile
    session["moblie"] = mobile
    session["user_id"] = user.id

    return jsonify(erron=RET.OK,errmsg="注册成功")



