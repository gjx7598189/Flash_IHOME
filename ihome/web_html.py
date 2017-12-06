# -*- coding:utf-8 -*-

from flask import Blueprint,current_app

html = Blueprint("html",__name__)


# 通过当前app来查找静态文件
@html.route('/<re(".*"):file_name>')
def get_html_file(file_name):

    if not file_name:

        file_name = "index.html"

    if file_name != "favicon.ico":
        file_name = "html/" + file_name
    return current_app.send_static_file(file_name)
