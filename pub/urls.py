# coding: utf-8

from pub import app
from pub import db

## 后台管理
from flask.ext.admin import Admin
admin = Admin(name=u'酒吧管理')
admin.init_app(app)

# 后台管理路径
from .views.admin_user import SuperUserView
from .views.admin_pub import PubView
admin.add_view(SuperUserView(db, name=u'管理员'))
admin.add_view(PubView(db, name=u'酒吧'))