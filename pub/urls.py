# coding: utf-8

from pub import app
from pub import db

from .views.admin_login import login_view, logout_view
from .views.admin_view import HomeView

## 后台管理
from flask.ext.admin import Admin
admin = Admin(name=u'猫吧客', index_view=HomeView())
admin.init_app(app)

# 用户登陆
app.add_url_rule('/login', 'login_view', login_view, methods=('GET', 'POST'))
app.add_url_rule('/logout', 'logout_view', logout_view, methods=('GET', 'POST'))

# 后台管理路径
from .views.admin_user import SuperUserView, ManagerUserView, UserView
from .views.admin_pub import PubView
from .views.admin_pub import SinglePubView
from .views.admin_ticket import TicketView

admin.add_view(SuperUserView(db, name=u'管理员', endpoint='superuser', category=u"猫吧客"))
admin.add_view(ManagerUserView(db, name=u'管理员', endpoint='manageruser', category=u"酒吧客户"))
admin.add_view(PubView(db, name=u'酒吧管理', endpoint='pubview'))
admin.add_view(SinglePubView(db, name=u'酒吧管理', endpoint='singlepubview'))
admin.add_view(UserView(db, name=u'会员管理'))
admin.add_view(TicketView(db, name=u'优惠券管理'))

# 微信接口处理路径
from .restful.verify import weixin
app.add_url_rule('/weixin/pub/<int:pub_id>', 'weixin', weixin, methods=('GET', 'POST'))

# 微信页面
from .views.web import pub_home
from .views.web import ticket_home
app.add_url_rule('/pub/<int:pub_id>', 'pub_home', pub_home, methods=('GET', 'POST'))
app.add_url_rule('/ticket/<int:ticket_id>', 'ticket_home', ticket_home, methods=('GET', 'POST'))
