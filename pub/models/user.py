# coding: utf-8

"""普通会员的类"""

from sqlalchemy import (Column, Integer, String, DATETIME, ForeignKey)
from sqlalchemy.orm import relationship

from .database import Base
from .pub import Pub
from ..utils.ex_password import generate_password
from ..utils.ex_time import todayfstr


class User(Base):
    """普通会员的类"""

    __tablename__ = 'admin_user'

    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(16), nullable=False, unique=True)
    admin = Column(String(4), nullable=False)
    password = Column(String(64), nullable=True)
    sign_up_date = Column(DATETIME, nullable=True)
    pub_id = Column(Integer, ForeignKey(Pub.id, ondelete='cascade', onupdate='cascade'), nullable=True)
    pub = relationship(Pub)

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.admin = kwargs.pop('admin')
        self.sign_up_date = todayfstr()
        self.password = self._set_password(kwargs.pop('password', None))
        self.pub_id = kwargs.pop('pub_id', None)

    def update(self, **kwargs):
        """更新用户数据的函数"""
        name = kwargs.pop('name', None)
        admin = kwargs.pop('admin', None)
        pub_id = kwargs.pop('pub_id', None)

        if name is not None:
            self.name = name
        if admin is not None:
            self.admin = admin
        if pub_id is not None:
            self.pub_id = pub_id
        self.password = self._update_password(kwargs.pop('password', None), self.password)

    def _set_password(self, password):
        """如果密码合法，返回加密后的密码，否则返回None"""
        if not self._valid_password(password):
            return None
        return generate_password(password)

    def _update_password(self, password, enc_password):
        if not self._valid_password(password):
            return enc_password
        if password != enc_password:  # 如果和之前的一样，说明没有变动
            return generate_password(password)
        return enc_password

    def _valid_password(self, password):
        """验证password合法性，不合法返回False，合法返回True"""
        if (password is None) or (not password.strip()):
            return False
        return True

    def check_password(self, new_password):
        """检查密码的正确性"""
        if not self._valid_password(new_password):
            return False
        if self.password == generate_password(new_password):
            return True
        return False

    def is_superuser(self):
        """猫吧超级超级管理员权限"""
        if self.admin == '1111':
            return True
        return False

    def is_normal_superuser(self):
        """猫吧普通管理员权限"""
        if self.admin == '1111' or self.admin == '1110':
            return True
        return False

    def is_manageruser(self):
        """酒吧超级管理员权限"""
        if self.admin == '111':
            return True
        return False

    def is_normal_manageruser(self):
        """酒吧普通管理员权限"""
        if self.admin == '111' or self.admin == '110':
            return True
        return False

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<AdminUser(name: %s)>' % self.name