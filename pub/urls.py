# coding: utf-8

from pub import app
from pub import db

from .views.admin_login import login_view, logout_view
from .views.admin_view import HomeView

## 后台管理
from flask.ext.admin import Admin
admin = Admin(name=u'酒吧管理', index_view=HomeView())
admin.init_app(app)

# 用户登陆
app.add_url_rule('/login', 'login_view', login_view, methods=('GET', 'POST'))
app.add_url_rule('/logout', 'logout_view', logout_view, methods=('GET', 'POST'))

# 后台管理路径
from .views.admin_user import SuperUserView, ManagerUserView
from .views.admin_pub import PubView
admin.add_view(SuperUserView(db, name=u'猫吧管理员', endpoint='superuser'))
admin.add_view(ManagerUserView(db, name=u'酒吧管理员', endpoint='manageruser'))
admin.add_view(PubView(db, name=u'酒吧管理'))