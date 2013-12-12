# coding: utf-8

"""创建数据库"""

from pub.models import Base, engine

# 必须import类，不然无法创建
from pub.models.pub import Pub
from pub.models.admin_user import AdminUser
from pub.models.user import User


if __name__ == '__main__':
    Base.metadata.create_all(engine)