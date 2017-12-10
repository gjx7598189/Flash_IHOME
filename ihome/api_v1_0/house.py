# -*- coding:utf-8 -*-

from flask import request,g,jsonify,current_app
from ihome.models import Area,Facility,User
from . import api
from ihome.utils.response_code import RET
from ihome import redis_store
from ihome.constants import AREA_INFO_REDIS_EXPIRES


@api.route("/areas")
def get_areas():

    # 先从redis中获取城区信息
    try:
        areas_array = redis_store.get("areas")
        if areas_array:
            return jsonify(erron=RET.OK,errmsg="OK",data={"areas":eval(areas_array)})
    except Exception as e:
        current_app.logger.error(e)


    # 获取所有的城区信息
    areas = Area.query.all()

    # 因为areas是一个对象的列表，不能直接返回，需要将其转成字典的列表
    areas_array = []
    for area in areas:
        areas_array.append(area.to_dict())

    # 将数据缓存到redis中
    try:
        redis_store.set("areas",areas_array,AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    # 数据返回
    return jsonify(erron=RET.OK,errmsg="OK",data={"areas":areas_array})