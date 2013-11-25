# coding: utf-8

from sqlalchemy import (Column, Integer, String, DATETIME, ForeignKey)
from sqlalchemy.orm import relationship

from .database import Base
from .pub import Pub
from ..utils.ex_password import generate_password, check_password
from ..utils.ex_time import todayfstr


class User(Base):
    """ 对应于数据库的user表格
    id
    name 用户名，如果是管理员就是普通用户名；如果是会员，一般都是手机号
    password 管理员登陆密码；会员没有密码，手机号就OK
    sign_up_date 用户注册时间
    admin 权限控制，不是二进制，纯粹的字符
        1111 超级管理员，就是能够管理所有酒吧的管理员
        1110 普通管理员

         111 酒吧超级管理员，一个酒吧的管理员
         110 酒吧普通管理员

          11 高级会员
          10 普通会员

    pub_id 酒吧ID
        超级管理员(1111 1110)没有pub_id，可以管理所有的酒吧
        其他的管理员(111 110)和会员(11 10)需要绑定到酒吧
        注：可以用户名相同，而pub_id不同账户
    wei_xin
        微信相关的资料
    birthday
        公立生日

    注：name和pub_id的组合不能重复
    """

    __tablename__ = 'user'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False)
    admin = Column(String(4), nullable=False)
    password = Column(String(64), nullable=True)
    sign_up_date = Column(DATETIME, nullable=True)
    pub_id = Column(Integer, ForeignKey(Pub.id, ondelete='cascade', onupdate='cascade'), nullable=True)
    pub = relationship(Pub)
    wei_xin = Column(String(64), nullable=True)
    birthday = Column(DATETIME, nullable=True)

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.admin = kwargs.pop('admin')
        self.sign_up_date = todayfstr()
        self.password = self._get_password(kwargs.pop('password', None))
        self.pub_id = kwargs.pop('pub_id', None)
        self.wei_xin = kwargs.pop('wei_xin', None)
        self.birthday = kwargs.pop('birthday', None)

    def update(self, **kwargs):
        """更新用户数据的函数"""
        self.name = kwargs.pop('name')
        self.admin = kwargs.pop('admin')
        self.password = self._get_password(kwargs.pop('password', None))
        self.pub_id = kwargs.pop('pub_id', None)
        self.wei_xin = kwargs.pop('wei_xin', None)
        self.birthday = kwargs.pop('birthday', None)


    def _get_password(self, password):
        """通过密码字符串生成加密的密码，如果密码为None，返回None"""

        if not password.strip():
            password = None

        if password is not None:
            return generate_password(password)

        return password

    def __repr__(self):
        return '<User(name: %s)>' % self.name