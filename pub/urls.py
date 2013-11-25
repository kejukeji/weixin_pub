# coding: utf-8

from flask.ext.admin import Admin

from pub import app


## 后台管理
admin = Admin(name=u'酒吧管理')
admin.init_app(app)