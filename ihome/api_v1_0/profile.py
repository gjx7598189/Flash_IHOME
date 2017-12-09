# -*- coding:utf-8 -*-

from . import api
from flask import request, current_app, jsonify,session,g
from ihome.utils.response_code import RET
from ihome.utils.storage_image import storage_image
from ihome.constants import QINIU_DOMIN_PREFIX
from ihome.models import User
from ihome.utils.commin import login_required
from ihome import db


@api.route("/user/auth")
@login_required
def get_user_auth():
    # 获取用户的实名认证信息
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询用户失败")
    if not user:
        return jsonify(erron=RET.USERERR,errmsg="用户不存在")
    return jsonify(erron=RET.OK,errmsg="OK",data=user.to_auth_dict())


@api.route("/user/avatar", methods=["POST"])
@login_required
def upload_avatar():

    # 使用装饰器来判断用户是否登陆@login_required
    # 获取上传的文件内容
    # 上传文件到七牛
    # 返回上传成功的图片地址

    # TODO 判断用户是否登陆

    # 获取上传的文件内容
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR, errmsg="请选择图片")

    # 上传文件到七牛
    try:
        key = storage_image(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.THIRDERR, errmsg="上传失败")

    # 取到用户的User模型，将上传成功的头像的地址保存到模型中并更新数据
    try:
        user = User.query.get(session["user_id"])
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询当前登陆用户失败")

    if not user:
        return jsonify(erron=RET.USERERR,errmsg="用户不存在")

    user.avatar_url = key
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollBack()
        return jsonify(erron=RET.DBERR,errmsg="保存头像失败")

    return jsonify(
        erron=RET.OK,
        errmsg="上传成功",
        data={
            "avatar_url": QINIU_DOMIN_PREFIX + key})


@api.route("/user/name",methods=["POST"])
@login_required
def set_user_name():

    # 使用装饰器来判断用户是否登陆@login_required
    # 获取传入的名字的参数，并判空
    # 取到当前登陆用户的ID并查询出对应的模型
    # 更新模型
    # 返回结果
    data_dict = request.json
    name = data_dict.get("name")
    if not name:
        return jsonify(erron=RET.PARAMERR,errmsg="参数不全")

    # 取到当前登陆用户的ID并查询出对应的模型
    # user_id = session.get("user_id")
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询数据失败")

    if not user:
        return jsonify(erron=RET.USERERR,errmsg="用户不存在")

    # 更新模型
    try:
        user.name = name
        db.session.commit()
    except Exception as e:
        db.session.rollBack()
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="用户保存失败")
    # 更新session中保存的用户名
    session["name"] = name
    # 返回结果
    return jsonify(erron=RET.OK,errmsg="修改成功")


@api.route("/user")
@login_required
def get_user_info():
    # 使用装饰器来判断用户是否登陆@login_required
    # 查询数据
    # 将用户模型指定的数据进行指定格式返回
    # user_id = session.get("user_id")
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询数据失败")

    if not user:
        return jsonify(erron=RET.USERERR,errmsg="用户不存在")

    # resp_data =
    return jsonify(erron=RET.OK,errmsg="OK",data=user.to_dict())
