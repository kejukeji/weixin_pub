# coding: utf-8

# flask 配置参数
DEBUG = True  # 是否启动调试功能
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmNui]LWX/,?RT^&556gh/ghj~hj/kh'  # session相关的密匙

# models 模块需要的配置参数
SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:3306/wei_xin_pub?charset=utf8'  # 连接的数据库
SQLALCHEMY_ECHO = True  # 输出语句