# coding: utf-8

from sqlalchemy import (Column, Integer, String, DATETIME)

from .database import Base
from .base_class import InitUpdate


class Pub(Base, InitUpdate):
    """ 对应于数据库的pub表格
    id
    name 酒吧的名字
    intro 基本介绍
    add_time 添加酒吧的时间
    """

    __tablename__ = 'pub'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    intro = Column(String(256), nullable=True)
    token = Column(String(128), nullable=True)
    token_time = Column(DATETIME, nullable=True)

    def __init__(self, **kwargs):
        self.init_value(('name',), kwargs)
        self.init_none(('intro',), kwargs)

    def update(self, **kwargs):
        self.update_value(('name', 'intro', 'token', 'token_time'), kwargs)

    def __repr__(self):
        return '<Pub(name: %s)>' % self.name