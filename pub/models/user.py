# coding: utf-8

"""普通会员的类"""

from sqlalchemy import (Column, Integer, String, DATETIME, ForeignKey)
from sqlalchemy.orm import relationship

from .database import Base
from .base_class import InitUpdate
from .pub import Pub
from ..utils.ex_time import todayfstr


class User(Base, InitUpdate):
    """普通会员的类
    name 会员的注册消息，比如电话号码什么的
    sign_up_date 注册时间
    pub_id 关联的酒吧
    open_id 用户的open_id
    """

    __tablename__ = 'user'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False, unique=True)
    sign_up_date = Column(DATETIME, nullable=True)
    pub_id = Column(Integer, ForeignKey(Pub.id, ondelete='cascade', onupdate='cascade'))
    pub = relationship(Pub)
    open_id = Column(String(128), nullable=False)

    def __init__(self, **kwargs):
        self.sign_up_date = todayfstr()
        self.init_value(('name', 'pub_id', 'open_id'), kwargs)

    def update(self, **kwargs):
        """更新用户数据的函数"""
        self.update_value(('name',), kwargs)