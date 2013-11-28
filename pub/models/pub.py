# coding: utf-8

from sqlalchemy import (Column, Integer, String)

from .database import Base


class Pub(Base):
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

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.intro = kwargs.pop('intro', None)

    def update(self, **kwargs):
        name = kwargs.pop('name', None)
        intro = kwargs.pop('intro', None)
        if name is not None:
            self.name = name
        if intro is not None:
            self.intro = intro

    def __repr__(self):
        return '<Pub(name: %s)>' % self.name