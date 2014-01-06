# coding: utf-8

from sqlalchemy import (Column, Integer, String, DATETIME, Boolean, ForeignKey)
from sqlalchemy.dialects.mysql import DOUBLE
from sqlalchemy.orm import relationship
from .database import Base
from .pub import Pub
from .base_class import InitUpdate
from ..utils.ex_time import todayfstr
from .user import User


class Gift(Base, InitUpdate):
    """
    id
    title 标题
    intro 介绍
    create_time 创建时间
    start_time 有效的开始时间
    stop_time 有效的结束时间
    win_number 中奖人数
    number 抽奖人数
    pub_id 优惠券隶属酒吧
    probability 中奖率 0-1
    最新创建的礼物作为礼品。。。如果没有礼品，显示为没有中奖！
    """

    __tablename__ = 'gift'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=False)
    intro = Column(String(256), nullable=False)
    create_time = Column(DATETIME, nullable=False)
    start_time = Column(DATETIME, nullable=False)
    stop_time = Column(DATETIME, nullable=False)
    win_number = Column(Integer, nullable=False, default=0, server_default='0')
    number = Column(Integer, nullable=False, default=0, server_default='0')
    pub_id = Column(Integer, ForeignKey(Pub.id, ondelete='cascade', onupdate='cascade'), nullable=False)
    probability = Column(DOUBLE, nullable=False, default=0, server_default='0')
    pub = relationship(Pub)

    def __init__(self, **kwargs):
        self.init_value(('title', 'intro', 'start_time', 'stop_time', 'pub_id', 'probability'), kwargs)
        self.create_time = todayfstr()

    def update(self, **kwargs):
        self.update_value(('title', 'intro', 'start_time', 'stop_time', 'probability'), kwargs)


class UserGift(Base, InitUpdate):
    """
    id
    gift_id
    user_id
    status 优惠券是否使用 0 没有使用 1 使用
    """

    __tablename__ = 'user_gift'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    gift_id = Column(Integer, ForeignKey(Gift.id, ondelete='cascade', onupdate='cascade'), nullable=False)
    gift = relationship(Gift)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='cascade', onupdate='cascade'), nullable=False)
    user = relationship(User)
    status = Column(Boolean, nullable=False, default=0, server_default='0')

    def __init__(self, **kwargs):
        self.init_value(('user_id', 'gift_id'), kwargs)

    def update(self, **kwargs):
        self.update_value(('status',), kwargs)


class UserGiftTime(Base, InitUpdate):
    """用户抽奖时间记录
    time 抽奖时间
    """
    __tablename__ = 'user_gift_time'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='cascade', onupdate='cascade'), nullable=False)
    time = Column(DATETIME, nullable=False)

    def __init__(self, **kwargs):
        self.init_value(('user_id', 'time'), kwargs)