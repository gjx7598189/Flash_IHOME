# -*- coding:utf-8 -*-

from . import api
from flask import request, current_app, jsonify,session
from ihome.utils.response_code import RET
from ihome.utils.storage_image import storage_image
from ihome.constants import QINIU_DOMIN_PREFIX
from ihome.models import User
from ihome import db


@api.route("/user/avatar", methods=["POST"])
def upload_avatar():

    # 判断用户是否登陆
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
