# -*- coding:utf-8 -*-

from flask import request,g,jsonify,current_app,session
from ihome.models import Area,Facility,User,House,HouseImage,Order
from . import api
from ihome.utils.response_code import RET
from ihome import redis_store,db
from ihome.constants import AREA_INFO_REDIS_EXPIRES,QINIU_DOMIN_PREFIX,HOUSE_DETAIL_REDIS_EXPIRE_SECOND,HOME_PAGE_MAX_HOUSES,HOME_PAGE_DATA_REDIS_EXPIRES
from ihome.constants import HOUSE_LIST_PAGE_CAPACITY
from ihome.utils.commin import login_required
from ihome.utils.storage_image import storage_image
from ihome import constants
import datetime


# 获取评论信息
@api.route("/orders/<order_id>/comment",methods=["PUT"])
@login_required
def comment_order(order_id):
    # 获取前端传过来的参数(comment评论的内容)
    # 通过id查询到指定的订单
    # 给该订单设置评论/将订单的内容设置成"完成"
    # 提交到数据库
    # 返回数据
    comment = request.json.get("comment")
    if not comment:
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")
    try:
        order = Order.query.filter(Order.id==order_id,Order.status=="WAIT_COMMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询数据库失败")

    if not order:
        return jsonify(erron=RET.NODATA,errmsg="订单不存在")

    # 给该订单设置评价/将订单的状态设置成"完成"
    order.comment = comment
    order.status = "COMPLETE"
    # 提交到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(erron=RET.DBERR,errmsg="数据保存失败")

    # 删除指定redis缓存
    try:
        house_id = order.house_id
        redis_store.delete("house_detail_%d"%house_id)
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(erron=RET.OK,errmsg="OK")


@api.route("/orders/<order_id>/status",methods=["PUT"])
@login_required
def change_order_status(order_id):
    # 更改订单的状态
    # 获取订单号
    # 获取订单号对应的订单模型
    # 检验订单的房东是否使登录用户
    # 修改订单状态:从待接单到待评论

    # 1.获取当前登录的用户ｉｄ
    user_id = g.user_id

    # 获取当前的是接单还是拒接
    action = request.json.get("action")
    # 校验参数
    if not action:
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")
    # action:accept/reject
    if action not in ("accept","reject"):
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")
    # 2.获取订单号对应的订单模型
    try:
        order = Order.query.filter(Order.id == order_id,Order.status == "WAIT_ACCEPT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询订单失败")

    if not order:
        return jsonify(erron=RET.NODATA,errmsg="订单不存在")
    # 3.检验订单的房东是否使登录用户
    if user_id != order.house.user_id:
        return jsonify(erron=RET.DBERR,errmsg="参数错误")

    # 4.修改订单状态:从待接单到待评论
    if "accept" == action:
        order.status = "WAIT_COMMENT"
    elif "reject" == action:
        order.status = "REJECTED"
        # 获取拒单原因
        reason = request.json.get("reason")
        if not reason:
            return jsonify(erron=RET.PARAMERR,errmsg="请填写据单原因")
        # 保存据单原因
        order.comment = reason
    # 提交数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(erron=RET.DBERR,errmsg="保存订单状态失败")

    return jsonify(erron=RET.OK,errmsg="OK")


@api.route("/orders",methods=["POST"])
@login_required
def add_order():
    # 获取参数(入住时间，离开时间，房屋id)
    # 判断参数是否符合规则
    # 判断是否符合该房屋
    # 判断该房间指定时间是否有订单
    # 创建订单模型
    # 保存订单
    # 返回结果
    data_dict = request.json
    start_date_str = data_dict.get("start_date")
    end_date_str = data_dict.get("end_date")
    house_id = data_dict.get("hid")
    # 判断参数是否符合规则
    if not all([start_date_str,end_date_str,house_id ]):
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")

    try:
        start_date = datetime.datetime.strptime(start_date_str,"%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        assert start_date < end_date, Exception("开始时间必须小于结束时间")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR,errmsg="参数数据")

    # 判断该房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="参数数据错误")
    if not house:
        return jsonify(erron=RET.NODATA,errmsg="该房屋不存在")

    # 判断该房屋指定时间是否有订单
    try:
        filters = [Order.house_id == house_id, Order.begin_date<end_date, Order.end_date>start_date]
        # 查询冲突订单的数据
        order_count = Order.query.filter(*filters).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR, errmsg="查询数据错误")
    if order_count > 0:
        return jsonify(erron=RET.DATAERR,errmsg="当前房屋已被预订")

    # 创建订单模型
    days = (end_date-start_date).days
    order = Order()
    order.user_id = g.user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price = house.price
    order.amount = house.price * days

    # 房屋的订单数据加1
    house.order_count += 1
    # 保存到数据库
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="保存数据失败")

    return jsonify(erron=RET.OK,errmsg="OK")


@api.route("/user/orders")
@login_required
def get_user_orders():
    # 查询当前用户所有订单
    # 获取当前用户ID

    # 获取当前用户ID
    user_id = g.user_id
    role = request.args.get("role")
    if not role:
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")
    if role not in ("custom","landlord"):
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")

    # 查询当前用户所有订单
    try:
        if role == "custom":
            orders = Order.query.filter(Order.user_id==user_id).order_by(Order.create_time.desc()).all()
        elif role == "landlord":
            houses = House.query.filter(House.user_id==user_id).all()
            # 获取到自己所有的房屋ID
            houses_id = [house.id for house in houses]
            orders = Order.query.filter(Order.house_id.in_(houses_id)).order_by(Order.create_time.desc()).all()

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询数据失败")

    order_dict = []
    for order in orders:
        order_dict.append(order.to_dict())

    return jsonify(erron=RET.OK,errmsg="OK",data={"orders":order_dict})
