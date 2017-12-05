# -*- coding:utf-8 -*-
import redis


class Config(object):

    SECRET_KEY = "ToPd1bzuQBXhj+eTinSv7cNtbrBNiA2mfb+NhooZNQ6F5CfxlqF0zdG0Knahfvd/"

    # 数据库
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome17"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PROT = '6379'

    # Session 扩展配置
    SESSION_TYPE = "redis"
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PROT)
    PERMANENT_SESSION_LIFETIME = 86400


class DevelopementConfig(Config):
    # 开发阶段所需要的配置
    DEBUG = True


class ProductionConfig(Config):
    # 生产环境所需配置
    pass

config = {
    "developement":DevelopementConfig,
    "production":ProductionConfig

}

