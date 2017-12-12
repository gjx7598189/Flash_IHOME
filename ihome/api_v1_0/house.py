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

# 前端房源请求的信息
# var params = {
#         aid:areaId,
#         sd:startDate,
#         ed:endDate,
#         sk:sortKey,
#         p:next_page
#     };


@api.route("/houses")
def search_house():
    # 查询除出所有房源信息并返回
    args = request.args
    # 区域ID
    aid = args.get("aid","")
    # 用户过滤的开始入住日期和结束入住日期
    start_data_str = args.get("sd","")
    end_data_str = args.get("ed","")
    sk = args.get("sk","new")
    p = args.get("p","1")

    # 判断参数
    start_data = None
    end_data = None
    try:
        if start_data_str:
            start_data = datetime.datetime.strptime(start_data_str,"%Y-%m-%d")
        if end_data_str:
            end_data = datetime.datetime.strptime(end_data_str,"%Y-%m-%d")
        if end_data and start_data:
            assert start_data < end_data,Exception("开始时间不能大于结束时间")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR,errmsg="参数有误")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR,errmsg="参数有误")
    # 从redis中读取房屋信息
    try:
        redis_key = "house_list_%s_%s_%s_%s"%(aid,start_data_str,end_data_str,sk)
        response_dict = redis_store.hget(redis_key,p)
        if response_dict:
            return jsonify(erron=RET.OK,errmsg="OK",data=eval(response_dict))
    except Exception as e:
        current_app.logger.error(e)


    try:
        house_query = House.query
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询房屋信息失败")

    filters = []
    if aid:
        # 添加过滤条件
        filters.append(House.area_id == aid)
    conflict_order = None
    if start_data and end_data:
        conflict_order = Order.query.filter(Order.begin_date<end_data,Order.end_date>start_data).all()
    elif start_data:
        conflict_order = Order.query.filter(Order.end_date>start_data).all()
    elif end_data:
        conflict_order = Order.query.filter(Order.begin_date<end_data).all()

    if conflict_order:
        # 获取冲突房间的ID
        conflict_house_ids = [order.house_id for order in conflict_order]
        # 不包含冲突订单的房屋id的数据
        filters.append(House.id.notin_(conflict_house_ids))
    # 跟库不同排序方式去查询
    if sk == "booking":
        house_query = house_query.filter(*filters).order_by(House.order_count.desc())
    elif sk == "price-inc":
        house_query = house_query.filter(*filters).order_by(House.price)
    elif sk == "price-dex":
        house_query = house_query.filter(*filters).order_by(House.price.desc())
    else:
        house_query = house_query.filter(*filters).order_by(House.create_time.desc())

    # 获取分页对象：参数1:第几页数据，参数2:每页加载几条数据，参数3:是否抛出错误
    paginate = house_query.paginate(int(p),HOUSE_LIST_PAGE_CAPACITY,False)
    # 取到当前页的所有对象
    houses = paginate.items
    # 记录总页数
    total_page = paginate.pages

    houses_dict =[]
    for house in houses:
        houses_dict.append(house.to_basic_dict())

    response_dict = {"houses":houses_dict,"total_page":total_page}
    # 保存房屋数据到redis中
    if p <= total_page: # 当前页小于或等于总页数再去保存
        try:
            redis_key = "house_list_%s_%s_%s_%s"%(aid,start_data_str,end_data_str,sk)
            # 获取管道操作
            pipe = redis_store.pipeline()
            # 开启事物
            pipe.multi()
            # 设置数据
            pipe.hset(redis_key,p,response_dict)
            # 设置过期时间
            pipe.expire(redis_key,constants.HOUSE_LIST_REDIS_EXPIRES)
            # 提交事物
            pipe.execute()
        except Exception as e:
            current_app.logger.error(e)

    return jsonify(erron=RET.OK,errmsg="OK",data=response_dict)


@api.route("/houses/index")
def get_houses_index():
    # 首页房屋推荐图最多5个，以定单数来排序(倒序)
    # 从缓存中获取
    try:
        house_dict = redis_store.get("home_house_index")
        if house_dict:
            return jsonify(erron=RET.OK,errmsg="OK",data=eval(house_dict))
    except Exception as e:
        current_app.logger.error(e)

    try:
        houses = House.query.order_by(House.order_count.desc()).limit(HOME_PAGE_MAX_HOUSES).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="数据查询失败")

    house_dict=[]
    if houses:
        for house in houses:
            house_dict.append(house.to_basic_dict())
        # 保存到缓存中
        try:
            redis_store.set("home_house_index",house_dict,HOME_PAGE_DATA_REDIS_EXPIRES)
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(erron=RET.OK,errmsg="OK",data=house_dict)
    return jsonify(erron=RET.OK,errmsg="OK",data=house_dict)


@api.route("/houses/<int:house_id>")
def get_house_detail(house_id):

    # 通过house_id查询出房屋
    # 将房屋模型的数据封装到字典中，
    # 直接返回
    # 将房屋数据缓存到redis

    user_id = session.get("user_id")

    # 先从redis缓存中获取数据
    try:
        house_dict = redis_store.get("house_detail_%d"%house_id)
        if house_dict:
            return jsonify(erron=RET.OK,errmsg="OK",data={"user_id":user_id,"house":eval(house_dict)})
    except Exception as e:
        current_app.logger.error(e)

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询数据失败")

    if not house:
        return jsonify(erron=RET.NODATA,errmsg="房屋不存在")

    # 生成返回数据
    house_dict = house.to_full_dict()

    # 将生成的数据存到redis缓存中
    redis_store.set("house_detail_%d"%house_id,house_dict,HOUSE_DETAIL_REDIS_EXPIRE_SECOND)

    return jsonify(erron=RET.OK,errmsg="OK",data={"user_id":user_id,"house":house_dict})


@api.route("/houses/<int:house_id>/images",methods=["POST"])
def upload_hose_image(house_id):

    # 获取参数，house_id,要上传的图片
    # 查询对应id的房屋
    # 在上传图片
    # 保存图片，判断房屋的首页图片是否有值，如果没有，设置
    try:
        housee_image_file = request.files.get("house_image").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR,errmsg="参数错误")

    # 查询是否有对应的房屋信息
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="查询房屋信息失败")
    if not house:
        return jsonify(erron=RET.NODATA,errmsg="房屋信息不存在")

    # 上传图片
    try:
        image_url = storage_image(housee_image_file)
    except Exception as e:
        current_app.looger.error(e)
        return jsonify(erron=RET.THIRDERR,errmsg="上传图片失败")

    # 初始化模型
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = image_url

    #设置房屋头图
    try:
        if not house.index_image_url:
            house.index_image_url = image_url

        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errom=RET.DBERR,errmsg="保存图片数据失败")

    return jsonify(erron=RET.OK,errmsg="OK",data={"url":QINIU_DOMIN_PREFIX + image_url})


@api.route("/houses",methods=["POST"])
@login_required
def save_new_house():
    # 获取上传的参数
    # 判断参数是否为空
    # 初始化House的对象
    # 返回结果
    # 前端发送过来的json数据
    '''
    {
        "title": "",
        "price": "",
        "area_id": "1",
        "address": "",
        "room_count": "",
        "acreage": "",
        "unit": "",
        "capacity": "",
        "beds": "",
        "deposit": "",
        "min_days": "",
        "max_days": "",
        "facility": ["7", "8"]
    }
    '''
    # 获取上传的参数
    user_id = g.user_id
    json_dict = request.json
    title = json_dict.get("title")
    price = json_dict.get("price")
    area_id = json_dict.get("area_id")
    address = json_dict.get("address")
    unit = json_dict.get("unit")
    room_count = json_dict.get("room_count")
    acreage = json_dict.get("acreage")
    capacity = json_dict.get("capacity")
    beds = json_dict.get("beds")
    deposit = json_dict.get("deposit")
    min_days = json_dict.get("min_days")
    max_days = json_dict.get("max_days")
    # 判断参数是否为空
    if not all([title,price,area_id,address,unit,room_count,acreage,capacity,beds,deposit,min_days,max_days]):
        return json_dict(erron=RET.PARAMERR,errmsg="参数不足")

    # 判断传入的价钱是否是数字，然后将其转为一分为单位的价格
    try:
        price = int(float(price)*100)
        deposit = int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(erron=RET.PARAMERR,errmsg="参数不足")


    # 初始化house对象
    house = House()

    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 设置房屋设施
    facilities = json_dict.get("facility")
    if facilities:
        house.facilities = Facility.query.filter(Facility.id.in_(facilities)).all()

    # 进行数据保存
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(erron=RET.DBERR,errmsg="添加数据失败")

    return jsonify(erron=RET.OK,errmsg="OK",data={"house_id":house.id})


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


