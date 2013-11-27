# coding: utf-8

"""后台添加新酒吧"""
import logging

from flask.ext.admin.contrib.sqla import ModelView
from flask import flash
from flask.ext.admin.babel import gettext
from wtforms.fields import TextField, PasswordField
from wtforms import validators

from ..models.pub import Pub
from ..models.user import User
from ..utils.others import form_to_dict

class PubView(ModelView):
    """后台添加酒吧和管理员视图"""

    page_size = 30

    def __init__(self, db, **kwargs):
        super(PubView, self).__init__(Pub, db, **kwargs)

    def scaffold_form(self):
        """改写form"""
        form_class = super(PubView, self).scaffold_form()
        form_class.user = TextField(label=u'酒吧管理员', validators=[validators.required()])
        form_class.password = PasswordField(label=u'管理员密码', validators=[validators.required()])

        return form_class

    def create_model(self, form):
        """添加酒吧和管理"""

        try:
            form_dict = form_to_dict(form)
            if not self._valid_form(form_dict):
                flash('用户名重复了，换一个呗', 'error')
                return False

            pub = self._get_pub(form_dict)
            self.session.add(pub)
            self.session.commit()

            user = self._get_user(form_dict, pub.id)
            self.session.add(user)
            self.session.commit()

        except Exception, ex:
            flash(gettext('Failed to create model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to create model')
            self.session.rollback()
            return False

        return True

    def _valid_form(self, form_dict):
        # 验证用户名是否重复
        if not self._has_user(form_dict['user']):
            return True

        return False

    def _has_user(self, user, admin='111', model=None):
        """检查用户是否存在，不存在返回False"""
        if model is None:
            return bool(User.query.filter(User.name == user).filter(User.admin == admin).count())
        else:
            return False # todo-lyw,这里需要继续编写

    def _get_user(self, form_dict, pub_id):
        """通过字典返回一个user类"""
        return User(name=form_dict['user'], password=form_dict['password'], admin='111', pub_id=pub_id)

    def _get_pub(self, form_dict):
        """通过字典返回一个pub类"""
        return Pub(name=form_dict['name'], intro=form_dict.get('intro', None))