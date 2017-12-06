# -*- coding:utf-8 -*-
# 验证码：包括图片验证和短信验证
from . import api
from flask import request,abort,current_app,jsonify,make_response
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from ihome.utils.response_code import RET


@api.route("/imagecode")
def get_image_code():
    """
    1. 取到图片编码
    2. 生成图片验证码
    3. 存储到redis中(key是图片编码，值是验证码的文字内容)
    4. 返回图片
    :return:
    """
    # 1. 取到图片编码
    args = request.args
    cur = args.get("cur")

    # 如果用户没有传图片id的话，直接抛错
    if not cur:
        abort(403)

    # 2. 生成图片验证码
    _, text, image = captcha.generate_captcha()
    # 为了测试输入到控制台中
    current_app.logger.debug(text)

    # 3. 存储到redis中(key是图片编码，值是验证码的文字内容)
    try:
        redis_store.set("ImageCode_"+cur, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 4. 返回验证码图片
    respnose = make_response(image)
    # TODO: 设置contentType
    return respnose