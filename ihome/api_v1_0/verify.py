# -*- coding:utf-8 -*-
# 验证码：包括图片验证和短信验证
import re
import random
from . import api
from flask import request, abort, current_app, jsonify, make_response, json
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.utils.sms import CCP

@api.route("/sms", methods=["POST"])
def send_sms():
    # 接受参数并判断是否为空
    # 判断手机号是否为空
    # 取到redis中缓冲的图片验证码内容
    # 对比图片验证码内容，如果对比成功
    # 发送短信验证码
    # 给前端响应结果

    data = request.data
    data_dict = json.loads(data)
    mobile = data_dict.get("mobile")
    image_code = data_dict.get("image_code")
    image_code_id = data_dict.get("image_code_id")

    # 判断接受参数是否为空
    if not all([mobile, image_code, image_code_id]):
        return jsonify(erron=RET.PARAMERR, errmsg="参数不全")
    # 判断手机格式是否合法
    if not re.match("^1[34578][0-9]{9}$", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机格式不正确")
    # 取到redis中缓冲的图片验证码内容
    try:
        real_image_code = redis_store.get("ImageCode_" + image_code_id)
        redis_store.delete("ImageCode_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg="获取验证码内容失败")
    if not real_image_code:
        return jsonify(erron=RET.NODATA,errmsg="验证码过期")

    # 对比图片验证码内容，如果对比成功
    if real_image_code.lower() != image_code.lower():
        return jsonify(erron=RET.DATAERR, errmsg="验证码不正确")
    # 判断手机号是否已经注册，如果注册直接返回错误
    try:
        user = User.query.filter_by(mobile=mobile).first()

    except Exception as e:
        user = None
        current_app.logger.error(e)
    if user:
        return jsonify(erron=RET.DATAEXIST,errmsg="数据已存在")

    # 发送短信验证码
    result = random.randint(0, 999999)
    sms_code = "%06d" % result
    current_app.logger.debug("%s短信验证号"%sms_code)
    # 发送
    # result = CCP().send_template_sms(
    #     mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    # if result == 0:
    #     return jsonify(erron=RET.THIRDERR, errmsg="发送验证码失败")
    # 保存验证码在redis中以便后续验证
    try:
        redis_store.set(
            "SMS_" + mobile,
            sms_code,
            constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg="验证码失败")
    # 发送成功
    return jsonify(erron=RET.OK, errmsg="发送成功")


@api.route("/imagecode")
def get_image_code():
    """
    1. 取到图片编码
    2. 生成图片验证码
    3. 存储到redis中(key是图片编码，值是验证码的文字内容)
    4. 返回图片
    """
    # 1. 取到图片编码
    args = request.args
    cur = args.get("cur")
    pre = args.get("pre")
    # 如果用户没有传图片id的话，直接抛错
    if not cur:
        abort(403)

    # 2. 生成图片验证码
    _, text, image = captcha.generate_captcha()
    # 为了测试输入到控制台中
    current_app.logger.debug(text)

    # 3. 存储到redis中(key是图片编码，值是验证码的文字内容)
    try:
        if pre:
            redis_store.delete("ImageCode_" + pre)
        redis_store.set(
            "ImageCode_" + cur,
            text,
            constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 4. 返回验证码图片
    respnose = make_response(image)
    # 设置contentType
    respnose.headers["Content-type"] = "image/jpg"
    return respnose
