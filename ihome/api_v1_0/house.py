# -*- coding:utf-8 -*-

from flask import request,g,jsonify
from ihome.models import Area,Facility,User
from . import api
from ihome.utils.response_code import RET

@api.route("/areas")
def get_areas():

    # 获取所有的城区信息
    areas = Area.query.all()

    # 因为areas是一个对象的列表，不能直接返回，需要将其转成字典的列表
    areas_array = []
    for area in areas:
        areas_array.append(area.to_dict())

    # 数据返回
    return jsonify(erron=RET.OK,errmsg="OK",data={"areas":areas_array})