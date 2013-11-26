# coding: utf-8

"""后台添加用户的视图"""
import logging

from flask.ext.admin.contrib.sqla import ModelView
from flask import flash
from flask.ext.admin.babel import gettext
from wtforms.fields import PasswordField

from ..models.user import User
from ..utils.others import form_to_dict
from ..utils.ex_object import delete_attrs


class SuperUserView(ModelView):
    """后台添加超级管理员的类"""

    page_size = 30
    form_overrides = dict(
        password=PasswordField
    )
    form_choices = dict(
        admin=[('1111', u'猫吧管理员')]
    )

    def __init__(self, db, **kwargs):
        super(SuperUserView, self).__init__(User, db, **kwargs)

    def scaffold_form(self):
        """改写form"""
        form_class = super(SuperUserView, self).scaffold_form()
        delete_attrs(form_class, ['pub', 'sign_up_date', 'wei_xin', 'birthday'])

        return form_class

    def create_model(self, form):
        try:
            if not bool(str(form.password.data)):
                flash('密码不能为空', 'error')
                return False
            if not self._valid_form(form):
                flash('用户名重复', 'error')
                return False
            model = self.model(**form_to_dict(form))
            self.session.add(model)
            self.session.commit()
        except Exception, ex:
            flash(gettext('Failed to create model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to create model')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, True)

        return True

    def update_model(self, form, model):
        try:
            if not self._valid_form(form, model=model):
                flash('用户名重复', 'error')
                return False
            model.update(**form_to_dict(form))
            self.session.commit()
        except Exception, ex:
            flash(gettext('Failed to update model. %(error)s', error=str(ex)), 'error')
            logging.exception('Failed to update model')
            self.session.rollback()
            return False
        else:
            self.after_model_change(form, model, False)

        return True

    def _valid_form(self, form, model=None):
        """检查form，放置用户名重复问题，添加猫吧超级管理员，那么用户名和管理员级别组合不能重复
        """
        form_dic = form_to_dict(form)
        if model is None:
            return not self._has_user(form_dic['name'], form_dic['admin'])
        else:
            if str(model.name) == form_dic['name']:
                return True
            return not self._has_user(form_dic['name'], form_dic['admin'])

    def _has_user(self, name, admin):
        """存在返回True，不存在返回False"""
        return bool(User.query.filter(User.name == name).filter(User.admin == admin).count())


class NormalUserView(ModelView):
    """后台添加酒吧管理员和普通会员的类"""
    pass