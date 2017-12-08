# -*- coding:utf-8 -*-

from flask import Blueprint, current_app, make_response
from flask_wtf.csrf import generate_csrf


html = Blueprint("html", __name__)


# 通过当前app来查找静态文件
@html.route('/<re(".*"):file_name>')
def get_html_file(file_name):

    if not file_name:

        file_name = "index.html"

    if file_name != "favicon.ico":
        file_name = "html/" + file_name

    # 生成csrf_token
    csrf_token = generate_csrf()
    # 添加csrf_token到cookie中
    response = make_response(current_app.send_static_file(file_name))
    response.set_cookie("csrf_token", csrf_token)
    return response
